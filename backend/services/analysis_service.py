"""
数据分析服务层

目标：
1. 先给数据库做画像，告诉前端这份数据适合做什么。
2. 再结合 STELLA 与 skills 生成分析规划。
3. 最后把分析任务执行结果统一成稳定协议，便于前台接入。
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

try:
    from scipy import stats as scipy_stats
except Exception:  # pragma: no cover - optional dependency at runtime
    scipy_stats = None

try:
    import statsmodels.api as sm
except Exception:  # pragma: no cover - optional dependency at runtime
    sm = None

from backend.services.database_service import DatabaseService
from backend.services.stella import stella_service
from backend.upload_models import (
    AnalysisConfig,
    AnalysisSuggestion,
    AnalysisTask,
    APICallLog,
    ColumnProfile,
    DatabaseProfile,
    ExternalAPIResponse,
)
from skills.registry import skill_registry

# 内存存储（生产环境应使用数据库）
analysis_tasks_db: Dict[str, AnalysisTask] = {}
api_logs_db: Dict[str, APICallLog] = {}

# 外部API配置
EXTERNAL_APIS = {
    "nhanes_analyzer": {
        "base_url": "https://nhanesanalyz-8bn77uby.manus.space/api",
        "endpoints": {"analyze": "/analyze", "visualize": "/visualize"},
    },
    "seer_analyzer": {
        "base_url": "https://seertotoponcology.vip/api",
        "endpoints": {"survival": "/survival-analysis", "incidence": "/incidence-analysis"},
    },
    "medivisual": {
        "base_url": "https://medivisual.org/api",
        "endpoints": {"chart": "/generate-chart", "dashboard": "/create-dashboard"},
    },
    "clawbio": {
        "base_url": "https://api.clawbio.com",
        "endpoints": {"pharmgx": "/pharmgx-analyze", "gwas": "/gwas-analyze", "scrna": "/scrna-analyze"},
    },
}


def _to_native(value: Any) -> Any:
    """把 numpy/pandas 对象转为 JSON 友好的 Python 原生对象。"""
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        if pd.isna(value) or np.isinf(value):
            return None
        return float(value)
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, list):
        return [_to_native(item) for item in value]
    if isinstance(value, tuple):
        return [_to_native(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _to_native(item) for key, item in value.items()}
    if pd.isna(value):
        return None
    return value


def _safe_round(value: Any, digits: int = 4) -> Optional[float]:
    native = _to_native(value)
    if native is None:
        return None
    if isinstance(native, (int, float)):
        return round(float(native), digits)
    return None


def _sample_values(series: pd.Series, limit: int = 5) -> List[Any]:
    values = []
    for item in series.dropna().head(limit).tolist():
        values.append(_to_native(item))
    return values


def _find_categorical_candidates(df: pd.DataFrame, max_categories: int = 10) -> List[str]:
    candidates: List[str] = []
    for column in df.columns:
        series = df[column]
        nunique = series.nunique(dropna=True)
        if nunique >= 2 and nunique <= max_categories and not pd.api.types.is_numeric_dtype(series):
            candidates.append(column)
    return candidates


def _find_numeric_candidates(df: pd.DataFrame) -> List[str]:
    return [column for column in df.columns if pd.api.types.is_numeric_dtype(df[column])]


class AnalysisService:
    """数据分析服务"""

    @classmethod
    async def create_analysis_task(
        cls,
        name: str,
        description: Optional[str],
        database_id: str,
        analysis_type: str,
        config: Optional[AnalysisConfig],
        created_by: Optional[str] = None,
    ) -> AnalysisTask:
        """创建分析任务"""

        database = DatabaseService.get_database(database_id)
        if not database:
            raise ValueError("数据库不存在")

        task_id = str(uuid.uuid4())
        now = datetime.utcnow()
        task = AnalysisTask(
            id=task_id,
            name=name,
            description=description,
            database_id=database_id,
            analysis_type=analysis_type,
            status="pending",
            config=config or AnalysisConfig(),
            created_by=created_by,
            created_at=now,
        )
        analysis_tasks_db[task_id] = task
        asyncio.create_task(cls._execute_analysis(task_id))
        return task

    @classmethod
    def get_task(cls, task_id: str) -> Optional[AnalysisTask]:
        return analysis_tasks_db.get(task_id)

    @classmethod
    def get_tasks(
        cls,
        database_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[AnalysisTask]:
        tasks = list(analysis_tasks_db.values())
        if database_id:
            tasks = [task for task in tasks if task.database_id == database_id]
        if status:
            tasks = [task for task in tasks if task.status == status]
        tasks.sort(key=lambda item: item.created_at, reverse=True)
        return tasks[skip : skip + limit]

    @classmethod
    async def profile_database(
        cls,
        database_id: str,
        sample_rows: int = 1000,
        max_categories: int = 10,
    ) -> DatabaseProfile:
        """生成数据库画像，用于前台分析规划和执行前检查。"""

        database = DatabaseService.get_database(database_id)
        if not database:
            raise ValueError("数据库不存在")

        df = await cls._load_dataframe(database)
        if df is None or df.empty:
            raise ValueError("无法加载数据或数据库为空")

        datetime_columns: List[str] = []
        for column in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[column]):
                datetime_columns.append(column)

        numeric_columns = _find_numeric_candidates(df)
        categorical_columns = [
            column
            for column in df.columns
            if column not in numeric_columns and column not in datetime_columns
        ]

        missingness = []
        column_profiles: List[ColumnProfile] = []
        for column in df.columns:
            series = df[column]
            missing_count = int(series.isna().sum())
            non_null_count = int(series.notna().sum())
            unique_count = int(series.nunique(dropna=True))
            missing_rate = round(missing_count / len(df), 4) if len(df) else 0.0

            if pd.api.types.is_numeric_dtype(series):
                inferred_role = "measure"
                numeric_summary = {
                    "mean": _safe_round(series.mean()),
                    "std": _safe_round(series.std()),
                    "min": _safe_round(series.min()),
                    "median": _safe_round(series.median()),
                    "max": _safe_round(series.max()),
                }
                categorical_summary = None
            elif pd.api.types.is_datetime64_any_dtype(series):
                inferred_role = "time"
                numeric_summary = None
                categorical_summary = {
                    "min": _to_native(series.min()),
                    "max": _to_native(series.max()),
                }
            else:
                if unique_count == len(df) and unique_count > 20:
                    inferred_role = "identifier"
                elif 2 <= unique_count <= max_categories:
                    inferred_role = "grouping_candidate"
                else:
                    inferred_role = "attribute"
                numeric_summary = None
                top_values = series.value_counts(dropna=True).head(5)
                categorical_summary = {
                    "top_values": [
                        {"value": _to_native(index), "count": int(count)}
                        for index, count in top_values.items()
                    ]
                }

            if missing_count > 0:
                missingness.append(
                    {
                        "column": column,
                        "missing_count": missing_count,
                        "missing_rate": missing_rate,
                    }
                )

            column_profiles.append(
                ColumnProfile(
                    name=column,
                    data_type=str(series.dtype),
                    inferred_role=inferred_role,
                    non_null_count=non_null_count,
                    missing_count=missing_count,
                    missing_rate=missing_rate,
                    unique_count=unique_count,
                    sample_values=_sample_values(series.head(sample_rows)),
                    numeric_summary=_to_native(numeric_summary) if numeric_summary else None,
                    categorical_summary=_to_native(categorical_summary) if categorical_summary else None,
                )
            )

        recommended_group_by = _find_categorical_candidates(df, max_categories=max_categories)
        recommended_targets = numeric_columns[:5]
        binary_candidates = [
            column
            for column in categorical_columns
            if 2 <= df[column].nunique(dropna=True) <= 2
        ]
        recommended_targets.extend(binary_candidates[:3])

        missingness.sort(key=lambda item: item["missing_rate"], reverse=True)
        return DatabaseProfile(
            database_id=database.id,
            database_name=database.name,
            total_rows=int(len(df)),
            total_columns=int(len(df.columns)),
            numeric_columns=numeric_columns,
            categorical_columns=categorical_columns,
            datetime_columns=datetime_columns,
            recommended_group_by=recommended_group_by[:5],
            recommended_targets=list(dict.fromkeys(recommended_targets))[:8],
            missingness_overview=missingness[:10],
            column_profiles=column_profiles,
            generated_at=datetime.utcnow(),
        )

    @classmethod
    async def build_analysis_plan(
        cls,
        database_id: str,
        objective: str,
        clinical_question: str,
        research_stage: Optional[str] = None,
        preferred_analysis_types: Optional[List[str]] = None,
        required_outputs: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """结合数据画像、STELLA 和 skills 生成分析规划。"""

        preferred_analysis_types = preferred_analysis_types or []
        required_outputs = required_outputs or []
        constraints = constraints or []

        profile = await cls.profile_database(database_id)
        stella_workflow = stella_service.build_workflow(
            objective=objective,
            clinical_question=clinical_question,
            research_stage=research_stage,
            required_outputs=required_outputs,
            constraints=constraints,
        )

        suggestions = cls._suggest_analyses(profile, preferred_analysis_types)
        recommended_skills = stella_workflow.get("recommended_skills", [])
        if len(recommended_skills) < 8:
            extra_skills = skill_registry.search_skills(f"{objective} {clinical_question}")
            seen = {item["id"] for item in recommended_skills}
            for skill in extra_skills:
                if skill.id in seen:
                    continue
                recommended_skills.append(
                    {
                        "id": skill.id,
                        "name": skill.name,
                        "category": skill.category.value,
                        "source": skill.source.value,
                        "wrapper_type": skill.wrapper_type,
                        "recommended_agent": skill.metadata.get("recommended_agent"),
                        "package_id": skill.package_id,
                    }
                )
                seen.add(skill.id)
                if len(recommended_skills) >= 8:
                    break

        recommended_agents = list(
            dict.fromkeys(
                [
                    skill.get("recommended_agent")
                    for skill in recommended_skills
                    if skill.get("recommended_agent")
                ]
            )
        )

        execution_notes = [
            f"数据共 {profile.total_rows} 行、{profile.total_columns} 列，先做 descriptive 建立数据全貌。",
            "只有当分组变量和目标变量稳定后，再进入 comparative / regression，避免在脏数据上直接做推断。",
            "STELLA 会把文献、临床问题和数据特征一起转成推荐技能与专家，不再只靠前台手动勾选。",
        ]
        if profile.missingness_overview:
            top_missing = profile.missingness_overview[0]
            execution_notes.append(
                f"当前缺失最严重的字段是 {top_missing['column']}，缺失率 {round(top_missing['missing_rate'] * 100, 2)}%，建议先确认缺失机制。"
            )

        return {
            "database_profile": profile.model_dump() if hasattr(profile, "model_dump") else profile.dict(),
            "stella_workflow": stella_workflow,
            "suggested_analyses": [
                suggestion.model_dump() if hasattr(suggestion, "model_dump") else suggestion.dict()
                for suggestion in suggestions
            ],
            "recommended_skills": recommended_skills,
            "recommended_agents": recommended_agents,
            "execution_notes": execution_notes,
        }

    @classmethod
    def _suggest_analyses(
        cls,
        profile: DatabaseProfile,
        preferred_analysis_types: List[str],
    ) -> List[AnalysisSuggestion]:
        suggestions: List[AnalysisSuggestion] = []
        preferred = {item.lower() for item in preferred_analysis_types}

        def allowed(analysis_type: str) -> bool:
            return not preferred or analysis_type in preferred

        if allowed("descriptive"):
            suggestions.append(
                AnalysisSuggestion(
                    analysis_type="descriptive",
                    title="先做描述性统计和数据质控",
                    rationale="任何真实研究数据在进入推断前，都需要先明确缺失、变量类型和分布。",
                    recommended_variables=profile.numeric_columns[:5] + profile.categorical_columns[:3],
                    estimated_outputs=["变量概览表", "缺失率摘要", "分布图建议"],
                )
            )

        if allowed("comparative") and profile.recommended_group_by and profile.numeric_columns:
            suggestions.append(
                AnalysisSuggestion(
                    analysis_type="comparative",
                    title="按分组变量做差异比较",
                    rationale="这份数据存在可用分组字段和连续变量，适合先做组间均值/比例比较。",
                    recommended_variables=profile.numeric_columns[:4],
                    group_by=profile.recommended_group_by[0],
                    estimated_outputs=["组间汇总表", "显著性检验", "均值比较图"],
                )
            )

        if allowed("correlation") and len(profile.numeric_columns) >= 2:
            suggestions.append(
                AnalysisSuggestion(
                    analysis_type="correlation",
                    title="先看变量之间的相关结构",
                    rationale="数值变量足够，可以先用相关性矩阵发现共线性和潜在线索。",
                    recommended_variables=profile.numeric_columns[:6],
                    estimated_outputs=["相关矩阵", "强相关变量对", "热图建议"],
                )
            )

        if allowed("regression") and profile.recommended_targets:
            target = profile.recommended_targets[0]
            candidate_predictors = [item for item in profile.numeric_columns if item != target][:6]
            if not candidate_predictors and profile.categorical_columns:
                candidate_predictors = profile.categorical_columns[:3]
            suggestions.append(
                AnalysisSuggestion(
                    analysis_type="regression",
                    title="进入多因素回归建模",
                    rationale="数据已有候选结局变量和协变量，可以直接形成回归分析骨架。",
                    recommended_variables=candidate_predictors,
                    target_variable=target,
                    group_by=profile.recommended_group_by[0] if profile.recommended_group_by else None,
                    estimated_outputs=["回归系数表", "显著性检验", "模型解释摘要"],
                )
            )

        if not suggestions:
            suggestions.append(
                AnalysisSuggestion(
                    analysis_type="custom",
                    title="先走自定义分析",
                    rationale="当前数据结构较特殊，建议先由 Agent 生成人工审核后的自定义分析规划。",
                    estimated_outputs=["数据画像", "人工分析建议"],
                )
            )

        return suggestions

    @classmethod
    async def _execute_analysis(cls, task_id: str):
        task = analysis_tasks_db.get(task_id)
        if not task:
            return

        task.status = "running"
        analysis_tasks_db[task_id] = task

        try:
            database = DatabaseService.get_database(task.database_id)
            if not database:
                raise ValueError("数据库不存在")

            df = await cls._load_dataframe(database)
            if df is None or df.empty:
                raise ValueError("无法加载数据")

            if task.analysis_type == "descriptive":
                result = await cls._descriptive_analysis(df, task.config)
            elif task.analysis_type == "comparative":
                result = await cls._comparative_analysis(df, task.config)
            elif task.analysis_type == "correlation":
                result = await cls._correlation_analysis(df, task.config)
            elif task.analysis_type == "regression":
                result = await cls._regression_analysis(df, task.config)
            else:
                result = await cls._custom_analysis(df, task.config)

            task.result = result
            task.status = "completed"
            task.completed_at = datetime.utcnow()
        except Exception as exc:
            task.status = "failed"
            task.error_message = str(exc)
            task.completed_at = datetime.utcnow()

        analysis_tasks_db[task_id] = task

    @classmethod
    async def _load_dataframe(cls, database) -> Optional[pd.DataFrame]:
        file_path = Path(database.file_path)
        file_type = database.file_type

        try:
            if file_type == "csv":
                return pd.read_csv(file_path)
            if file_type in ["xlsx", "xls"]:
                return pd.read_excel(file_path)
            if file_type == "json":
                import json

                with open(file_path, "r", encoding="utf-8") as handle:
                    data = json.load(handle)
                return pd.DataFrame(data if isinstance(data, list) else [data])
            if file_type in ["sqlite", "db"]:
                import sqlite3

                conn = sqlite3.connect(str(file_path))
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                table_name = cursor.fetchone()[0]
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                conn.close()
                return df
            return None
        except Exception as exc:
            print(f"加载数据失败: {exc}")
            return None

    @classmethod
    def _build_result(
        cls,
        analysis_type: str,
        headline: str,
        statistics: Optional[Dict[str, Any]] = None,
        tables: Optional[List[Dict[str, Any]]] = None,
        charts: Optional[List[Dict[str, Any]]] = None,
        recommendations: Optional[List[str]] = None,
        extra_summary: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        summary = {
            "analysis_type": analysis_type,
            "headline": headline,
            "generated_at": datetime.utcnow().isoformat(),
        }
        if extra_summary:
            summary.update(_to_native(extra_summary))
        return {
            "analysis_type": analysis_type,
            "summary": _to_native(summary),
            "statistics": _to_native(statistics or {}),
            "tables": _to_native(tables or []),
            "charts": _to_native(charts or []),
            "recommendations": recommendations or [],
        }

    @classmethod
    async def _descriptive_analysis(cls, df: pd.DataFrame, config: AnalysisConfig) -> Dict[str, Any]:
        variables = [column for column in (config.variables or df.columns.tolist()) if column in df.columns]
        if not variables:
            variables = df.columns.tolist()

        numeric_summary: Dict[str, Dict[str, Any]] = {}
        numeric_rows: List[Dict[str, Any]] = []
        categorical_summary: Dict[str, Dict[str, Any]] = {}
        categorical_rows: List[Dict[str, Any]] = []

        for column in variables:
            series = df[column]
            missing_count = int(series.isna().sum())
            if pd.api.types.is_numeric_dtype(series):
                stats = {
                    "count": int(series.count()),
                    "mean": _safe_round(series.mean()),
                    "std": _safe_round(series.std()),
                    "min": _safe_round(series.min()),
                    "median": _safe_round(series.median()),
                    "max": _safe_round(series.max()),
                    "missing": missing_count,
                }
                numeric_summary[column] = stats
                numeric_rows.append({"variable": column, **stats})
            else:
                top_values = series.value_counts(dropna=True).head(5)
                summary = {
                    "unique_count": int(series.nunique(dropna=True)),
                    "missing": missing_count,
                    "top_values": [
                        {"value": _to_native(index), "count": int(count)}
                        for index, count in top_values.items()
                    ],
                }
                categorical_summary[column] = summary
                categorical_rows.append(
                    {
                        "variable": column,
                        "unique_count": summary["unique_count"],
                        "missing": missing_count,
                        "top_value": summary["top_values"][0]["value"] if summary["top_values"] else None,
                    }
                )

        missingness = sorted(
            [
                {
                    "variable": column,
                    "missing_rate": round(float(df[column].isna().mean()), 4),
                    "missing_count": int(df[column].isna().sum()),
                }
                for column in variables
            ],
            key=lambda item: item["missing_rate"],
            reverse=True,
        )

        recommendations = ["先确认高缺失变量是否需要剔除或插补。"]
        if categorical_rows:
            recommendations.append("分类型字段已识别，可直接进入 comparative 分析。")
        if len(numeric_rows) >= 2:
            recommendations.append("数值变量足够，下一步可进入 correlation 或 regression。")

        return cls._build_result(
            "descriptive",
            "已完成数据画像与描述性统计。",
            statistics={
                "total_rows": int(len(df)),
                "total_columns": int(len(df.columns)),
                "numeric_summary": numeric_summary,
                "categorical_summary": categorical_summary,
                "missingness_overview": missingness[:10],
            },
            tables=[
                {"name": "numeric_summary", "title": "数值变量统计表", "rows": numeric_rows},
                {"name": "categorical_summary", "title": "分类变量统计表", "rows": categorical_rows},
            ],
            charts=[
                {
                    "type": "bar",
                    "title": "缺失率最高变量",
                    "x": [item["variable"] for item in missingness[:5]],
                    "y": [item["missing_rate"] for item in missingness[:5]],
                }
            ],
            recommendations=recommendations,
            extra_summary={"rows": int(len(df)), "columns": int(len(df.columns))},
        )

    @classmethod
    async def _comparative_analysis(cls, df: pd.DataFrame, config: AnalysisConfig) -> Dict[str, Any]:
        group_by = config.group_by
        if not group_by or group_by not in df.columns:
            return cls._build_result(
                "comparative",
                "缺少有效的分组变量，暂时无法执行比较分析。",
                recommendations=["请先指定 config.group_by，并确保该字段是 2-10 类的分组变量。"],
            )

        variables = [item for item in (config.variables or df.columns.tolist()) if item in df.columns]
        numeric_vars = [item for item in variables if pd.api.types.is_numeric_dtype(df[item])]
        if not numeric_vars:
            return cls._build_result(
                "comparative",
                "没有找到可比较的数值变量。",
                recommendations=["请至少选择一个数值型变量用于组间比较。"],
            )

        grouped = df.groupby(group_by, dropna=False)
        group_levels = [str(level) for level in grouped.groups.keys()]
        rows: List[Dict[str, Any]] = []
        stats_payload: Dict[str, Any] = {}

        for variable in numeric_vars[:8]:
            per_group = grouped[variable].agg(["count", "mean", "std", "median"]).reset_index()
            per_group_records = per_group.to_dict("records")
            test_result = None
            arrays = [group[variable].dropna().astype(float).values for _, group in grouped]
            arrays = [arr for arr in arrays if len(arr) > 1]

            if scipy_stats and len(arrays) == 2:
                stat, p_value = scipy_stats.ttest_ind(arrays[0], arrays[1], equal_var=False)
                test_result = {"test": "t_test", "statistic": _safe_round(stat), "p_value": _safe_round(p_value)}
            elif scipy_stats and len(arrays) > 2:
                stat, p_value = scipy_stats.f_oneway(*arrays)
                test_result = {"test": "anova", "statistic": _safe_round(stat), "p_value": _safe_round(p_value)}

            stats_payload[variable] = {"by_group": _to_native(per_group_records), "test": test_result}
            for record in per_group_records:
                rows.append({"variable": variable, **_to_native(record), "test": test_result})

        recommendations = [
            f"当前建议优先围绕 {group_by} 做组间比较。",
            "若显著性成立，可继续进入 regression 做多因素调整。",
        ]
        return cls._build_result(
            "comparative",
            f"已完成按 {group_by} 的组间比较。",
            statistics={"group_by": group_by, "group_levels": group_levels, "comparisons": stats_payload},
            tables=[{"name": "group_comparison", "title": "组间比较结果", "rows": rows}],
            charts=[
                {
                    "type": "grouped_bar",
                    "title": f"{group_by} 组间均值比较",
                    "group_by": group_by,
                    "variables": numeric_vars[:4],
                }
            ],
            recommendations=recommendations,
            extra_summary={"group_by": group_by, "groups": group_levels},
        )

    @classmethod
    async def _correlation_analysis(cls, df: pd.DataFrame, config: AnalysisConfig) -> Dict[str, Any]:
        variables = [item for item in (config.variables or df.columns.tolist()) if item in df.columns]
        numeric_vars = [item for item in variables if pd.api.types.is_numeric_dtype(df[item])]
        if len(numeric_vars) < 2:
            return cls._build_result(
                "correlation",
                "数值变量不足，暂时无法执行相关性分析。",
                recommendations=["请至少提供两个数值型变量。"],
            )

        corr_matrix = df[numeric_vars].corr()
        strong_correlations = []
        for left_index in range(len(numeric_vars)):
            for right_index in range(left_index + 1, len(numeric_vars)):
                corr = corr_matrix.iloc[left_index, right_index]
                if abs(corr) > 0.5:
                    strong_correlations.append(
                        {
                            "var1": numeric_vars[left_index],
                            "var2": numeric_vars[right_index],
                            "correlation": _safe_round(corr),
                            "strength": "strong" if abs(corr) > 0.7 else "moderate",
                        }
                    )
        strong_correlations.sort(key=lambda item: abs(item["correlation"] or 0), reverse=True)

        recommendations = [
            "强相关变量进入回归前建议检查共线性。",
            "若存在明确结局变量，可把强相关变量优先纳入多因素模型。",
        ]
        return cls._build_result(
            "correlation",
            "已完成变量相关结构分析。",
            statistics={
                "variables": numeric_vars,
                "correlation_matrix": corr_matrix.to_dict(),
                "strong_correlations": strong_correlations,
            },
            tables=[{"name": "strong_correlations", "title": "强相关变量对", "rows": strong_correlations}],
            charts=[
                {"type": "heatmap", "title": "相关矩阵热图", "variables": numeric_vars},
            ],
            recommendations=recommendations,
            extra_summary={"strong_pairs": len(strong_correlations)},
        )

    @classmethod
    async def _regression_analysis(cls, df: pd.DataFrame, config: AnalysisConfig) -> Dict[str, Any]:
        target = config.target_variable
        numeric_candidates = _find_numeric_candidates(df)
        if not target:
            target = numeric_candidates[0] if numeric_candidates else None
        if not target or target not in df.columns:
            return cls._build_result(
                "regression",
                "缺少可用结局变量，暂时无法执行回归分析。",
                recommendations=["请在 config.target_variable 里明确指定结局变量。"],
            )

        covariates = [item for item in (config.covariates or config.variables or []) if item in df.columns and item != target]
        if not covariates:
            covariates = [item for item in numeric_candidates if item != target][:6]
        if not covariates:
            categorical_candidates = _find_categorical_candidates(df, max_categories=config.max_categories)
            covariates = [item for item in categorical_candidates if item != target][:3]
        if not covariates:
            return cls._build_result(
                "regression",
                "没有可用协变量，暂时无法执行回归分析。",
                recommendations=["请在 config.covariates 中明确指定协变量。"],
            )

        frame = df[[target] + covariates].copy().dropna()
        if len(frame) < max(20, len(covariates) * 5):
            return cls._build_result(
                "regression",
                "有效样本不足，不建议直接进入回归。",
                recommendations=[f"当前有效样本仅 {len(frame)} 行，建议先补齐数据或减少协变量数量。"],
                extra_summary={"effective_rows": int(len(frame))},
            )

        y = frame[target]
        mode = "linear"
        target_mapping = None
        if pd.api.types.is_bool_dtype(y):
            y = y.astype(int)
            mode = "logistic"
        elif not pd.api.types.is_numeric_dtype(y):
            unique_values = list(pd.Series(y).dropna().unique())
            if len(unique_values) == 2:
                target_mapping = {str(unique_values[0]): 0, str(unique_values[1]): 1}
                y = y.map(target_mapping).astype(float)
                mode = "logistic"
            else:
                return cls._build_result(
                    "regression",
                    "当前结局变量不是数值型，也不是二分类变量。",
                    recommendations=["请更换 target_variable，或先把结局变量整理为连续型/二分类。"],
                )

        X = pd.get_dummies(frame[covariates], drop_first=True)
        numeric_X = X.select_dtypes(include=[np.number, bool]).astype(float)
        if numeric_X.empty:
            return cls._build_result(
                "regression",
                "协变量编码后为空，无法建模。",
                recommendations=["请优先使用数值变量或低基数分类变量作为协变量。"],
            )

        coefficients: List[Dict[str, Any]] = []
        metrics: Dict[str, Any] = {"mode": mode, "target_variable": target, "covariates": covariates}

        try:
            if sm is None:
                raise RuntimeError("statsmodels 不可用")

            design_matrix = sm.add_constant(numeric_X, has_constant="add")
            response = y.astype(float)
            if mode == "logistic":
                model = sm.Logit(response, design_matrix).fit(disp=0)
                metrics["pseudo_r2"] = _safe_round(model.prsquared)
            else:
                model = sm.OLS(response, design_matrix).fit()
                metrics["r_squared"] = _safe_round(model.rsquared)
                metrics["adj_r_squared"] = _safe_round(model.rsquared_adj)

            conf_int = model.conf_int()
            for name, coefficient in model.params.items():
                coefficients.append(
                    {
                        "term": str(name),
                        "coefficient": _safe_round(coefficient),
                        "p_value": _safe_round(model.pvalues.get(name)),
                        "ci_low": _safe_round(conf_int.loc[name, 0]) if name in conf_int.index else None,
                        "ci_high": _safe_round(conf_int.loc[name, 1]) if name in conf_int.index else None,
                    }
                )
        except Exception as exc:
            return cls._build_result(
                "regression",
                "回归建模失败，建议先检查目标变量和协变量质量。",
                recommendations=[f"建模错误: {exc}", "建议先运行 descriptive / correlation，清理异常值后再试。"],
            )

        coefficients_sorted = sorted(
            coefficients,
            key=lambda item: abs(item["coefficient"] or 0),
            reverse=True,
        )
        recommendations = [
            f"当前模型类型为 {mode} regression，可先审阅 p 值显著的协变量。",
            "若模型用于发表，建议在前台继续接上敏感性分析和共线性检查。",
        ]
        if target_mapping:
            recommendations.append(f"二分类目标已按 {target_mapping} 编码。")

        return cls._build_result(
            "regression",
            f"已完成 {mode} regression 建模。",
            statistics=metrics,
            tables=[{"name": "coefficients", "title": "回归系数表", "rows": coefficients_sorted}],
            charts=[
                {
                    "type": "coefficient_bar",
                    "title": "主要协变量系数",
                    "x": [item["term"] for item in coefficients_sorted[:8]],
                    "y": [item["coefficient"] for item in coefficients_sorted[:8]],
                }
            ],
            recommendations=recommendations,
            extra_summary={"effective_rows": int(len(frame)), "mode": mode},
        )

    @classmethod
    async def _custom_analysis(cls, df: pd.DataFrame, config: AnalysisConfig) -> Dict[str, Any]:
        profile_like = {
            "rows": int(len(df)),
            "columns": int(len(df.columns)),
            "numeric_columns": _find_numeric_candidates(df),
            "categorical_candidates": _find_categorical_candidates(df, max_categories=config.max_categories),
        }
        return cls._build_result(
            "custom",
            "已生成自定义分析起点，等待前台或真人继续选择。",
            statistics=profile_like,
            recommendations=[
                "建议先调用 /api/analysis/plan 生成研究问题导向的分析规划。",
                "如果这是上传后的首轮分析，先跑 descriptive 再决定下一步。",
            ],
        )

    @classmethod
    async def call_external_api(
        cls,
        database_id: str,
        api_provider: str,
        endpoint: str,
        parameters: Dict[str, Any],
        callback_url: Optional[str] = None,
    ) -> ExternalAPIResponse:
        if api_provider not in EXTERNAL_APIS:
            raise ValueError(f"不支持的API提供商: {api_provider}")

        database = DatabaseService.get_database(database_id)
        if not database:
            raise ValueError("数据库不存在")

        task_id = str(uuid.uuid4())
        log_id = str(uuid.uuid4())
        api_log = APICallLog(
            id=log_id,
            task_id=task_id,
            api_name=api_provider,
            endpoint=endpoint,
            request_data={"database_id": database_id, "parameters": parameters},
            created_at=datetime.utcnow(),
        )
        api_logs_db[log_id] = api_log

        task = AnalysisTask(
            id=task_id,
            name=f"External API: {api_provider}",
            description=f"调用 {api_provider} 的 {endpoint}",
            database_id=database_id,
            analysis_type="external_api",
            status="running",
            config=AnalysisConfig(),
            created_at=datetime.utcnow(),
        )
        analysis_tasks_db[task_id] = task

        asyncio.create_task(
            cls._execute_external_api_call(task_id, log_id, api_provider, endpoint, parameters, database)
        )

        return ExternalAPIResponse(
            task_id=task_id,
            status="running",
            external_job_id=f"{api_provider}_{task_id}",
            estimated_duration=60,
            message="外部API调用已启动",
        )

    @classmethod
    async def _execute_external_api_call(
        cls,
        task_id: str,
        log_id: str,
        api_provider: str,
        endpoint: str,
        parameters: Dict[str, Any],
        database,
    ):
        import time

        task = analysis_tasks_db.get(task_id)
        api_log = api_logs_db.get(log_id)
        if not task or not api_log:
            return

        start_time = time.time()
        try:
            await asyncio.sleep(2)
            task.result = cls._build_result(
                "external_api",
                f"{api_provider} 已完成外部分析。",
                statistics={
                    "api_provider": api_provider,
                    "endpoint": endpoint,
                    "data_processed": database.row_count,
                },
                recommendations=["可把外部 API 结果与平台内部分析结果并排展示。"],
                extra_summary={"provider": api_provider, "endpoint": endpoint},
            )
            task.status = "completed"
            task.completed_at = datetime.utcnow()
            api_log.response_data = task.result
            api_log.status_code = 200
        except Exception as exc:
            task.status = "failed"
            task.error_message = str(exc)
            task.completed_at = datetime.utcnow()
            api_log.response_data = {"error": str(exc)}
            api_log.status_code = 500
        finally:
            api_log.duration_ms = int((time.time() - start_time) * 1000)
            analysis_tasks_db[task_id] = task
            api_logs_db[log_id] = api_log
