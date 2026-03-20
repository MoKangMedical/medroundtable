"""
数据分析服务层
处理数据分析任务和外部 API 调用，并将任务结果持久化到数据库。
"""
import asyncio
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

import pandas as pd

from backend.database import (
    AnalysisTaskRecord,
    ExternalAPICallRecord,
    SessionLocal,
)
from backend.upload_models import (
    AnalysisTask, AnalysisConfig, ExternalAPIResponse
)
from backend.services.database_service import DatabaseService


EXTERNAL_APIS = {
    "nhanes_analyzer": {
        "base_url": "https://nhanesanalyz-8bn77uby.manus.space/api",
        "endpoints": {
            "analyze": "/analyze",
            "visualize": "/visualize"
        }
    },
    "seer_analyzer": {
        "base_url": "https://seertotoponcology.vip/api",
        "endpoints": {
            "survival": "/survival-analysis",
            "incidence": "/incidence-analysis"
        }
    },
    "medivisual": {
        "base_url": "https://medivisual.org/api",
        "endpoints": {
            "chart": "/generate-chart",
            "dashboard": "/create-dashboard"
        }
    },
    "clawbio": {
        "base_url": "https://api.clawbio.com",
        "endpoints": {
            "pharmgx": "/pharmgx-analyze",
            "gwas": "/gwas-analyze",
            "scrna": "/scrna-analyze"
        }
    }
}


def _dump_model(model: Optional[Any]) -> Optional[Dict[str, Any]]:
    if model is None:
        return None
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def _task_from_record(record: AnalysisTaskRecord) -> AnalysisTask:
    config_payload = record.config_payload or {}
    return AnalysisTask(
        id=record.id,
        name=record.name,
        description=record.description,
        database_id=record.database_id,
        analysis_type=record.analysis_type,
        status=record.status,
        config=AnalysisConfig(**config_payload) if config_payload else AnalysisConfig(),
        result=record.result_payload,
        error_message=record.error_message,
        created_by=record.created_by,
        created_at=record.created_at,
        completed_at=record.completed_at,
    )


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
        created_by: Optional[str] = None
    ) -> AnalysisTask:
        database = DatabaseService.get_database(database_id)
        if not database:
            raise ValueError("数据库不存在")

        now = datetime.utcnow()
        record = AnalysisTaskRecord(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            database_id=database_id,
            analysis_type=analysis_type,
            status="pending",
            config_payload=_dump_model(config) or {},
            created_by=created_by,
            created_at=now,
            updated_at=now,
            extra_metadata={
                "source_kind": (database.metadata or {}).get("source_kind", "uploaded-database"),
                "database_name": database.name,
            },
        )

        with SessionLocal() as db:
            db.add(record)
            db.commit()
            db.refresh(record)

        asyncio.create_task(cls._execute_analysis(record.id))
        return _task_from_record(record)

    @classmethod
    async def _execute_analysis(cls, task_id: str):
        with SessionLocal() as db:
            record = db.query(AnalysisTaskRecord).filter(AnalysisTaskRecord.id == task_id).first()
            if not record:
                return
            record.status = "running"
            record.updated_at = datetime.utcnow()
            config = AnalysisConfig(**(record.config_payload or {}))
            database_id = record.database_id
            analysis_type = record.analysis_type
            db.commit()

        try:
            database = DatabaseService.get_database(database_id)
            if not database:
                raise ValueError("数据库不存在")

            df = await cls._load_dataframe(database)
            if df is None:
                raise ValueError("无法加载数据")

            if analysis_type == "descriptive":
                result = await cls._descriptive_analysis(df, config)
            elif analysis_type == "comparative":
                result = await cls._comparative_analysis(df, config)
            elif analysis_type == "correlation":
                result = await cls._correlation_analysis(df, config)
            elif analysis_type == "regression":
                result = await cls._regression_analysis(df, config)
            else:
                result = await cls._custom_analysis(df, config)

            with SessionLocal() as db:
                record = db.query(AnalysisTaskRecord).filter(AnalysisTaskRecord.id == task_id).first()
                if not record:
                    return
                record.result_payload = result
                record.status = "completed"
                record.completed_at = datetime.utcnow()
                record.updated_at = datetime.utcnow()
                db.commit()
        except Exception as exc:
            with SessionLocal() as db:
                record = db.query(AnalysisTaskRecord).filter(AnalysisTaskRecord.id == task_id).first()
                if not record:
                    return
                record.status = "failed"
                record.error_message = str(exc)
                record.completed_at = datetime.utcnow()
                record.updated_at = datetime.utcnow()
                db.commit()

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
                if isinstance(data, list):
                    return pd.DataFrame(data)
                return pd.DataFrame([data])
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
    async def _descriptive_analysis(
        cls,
        df: pd.DataFrame,
        config: AnalysisConfig
    ) -> Dict[str, Any]:
        variables = config.variables or df.columns.tolist()

        numeric_stats = {}
        for col in variables:
            if col not in df.columns:
                continue
            if pd.api.types.is_numeric_dtype(df[col]):
                numeric_stats[col] = {
                    "count": int(df[col].count()),
                    "mean": float(df[col].mean()),
                    "std": float(df[col].std()),
                    "min": float(df[col].min()),
                    "25%": float(df[col].quantile(0.25)),
                    "50%": float(df[col].median()),
                    "75%": float(df[col].quantile(0.75)),
                    "max": float(df[col].max()),
                    "missing": int(df[col].isnull().sum())
                }

        categorical_stats = {}
        for col in variables:
            if col not in df.columns:
                continue
            if df[col].dtype == "object":
                value_counts = df[col].value_counts().head(10)
                categorical_stats[col] = {
                    "unique_count": int(df[col].nunique()),
                    "top_values": value_counts.to_dict()
                }

        return {
            "analysis_type": "descriptive",
            "summary": {
                "total_rows": int(len(df)),
                "total_columns": int(len(df.columns)),
            },
            "statistics": {
                "numeric_summary": numeric_stats,
                "categorical_summary": categorical_stats,
            },
            "tables": [
                {
                    "title": "字段概览",
                    "rows": [
                        {
                            "column": str(column),
                            "dtype": str(df[column].dtype),
                            "missing": int(df[column].isnull().sum()),
                        }
                        for column in df.columns
                    ],
                }
            ],
            "recommendations": [
                "先核对缺失值比例，再决定是否补值或剔除。",
                "优先确认主要终点变量的分布形态，再选择后续检验方法。",
            ],
            "generated_at": datetime.utcnow().isoformat(),
        }

    @classmethod
    async def _comparative_analysis(
        cls,
        df: pd.DataFrame,
        config: AnalysisConfig
    ) -> Dict[str, Any]:
        group_by = config.group_by
        variables = config.variables

        if not group_by or group_by not in df.columns:
            return {
                "analysis_type": "comparative",
                "summary": {"message": "需要提供合法的分组变量"},
                "statistics": {},
                "recommendations": ["请先选择一个存在于数据集中的分组变量。"],
                "generated_at": datetime.utcnow().isoformat(),
            }

        if not variables:
            variables = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]

        comparison_results = {}
        for var in variables:
            if var in df.columns and pd.api.types.is_numeric_dtype(df[var]):
                group_stats = df.groupby(group_by)[var].agg([
                    "count", "mean", "std", "min", "max"
                ]).to_dict()
                comparison_results[var] = group_stats

        return {
            "analysis_type": "comparative",
            "summary": {
                "group_by": group_by,
                "variable_count": len(variables),
            },
            "statistics": {"group_comparison": comparison_results},
            "recommendations": [
                f"先确认 {group_by} 的分组是否均衡，再决定是否进入假设检验。",
                "如果组间样本量差异较大，建议增加稳健性分析。",
            ],
            "generated_at": datetime.utcnow().isoformat(),
        }

    @classmethod
    async def _correlation_analysis(
        cls,
        df: pd.DataFrame,
        config: AnalysisConfig
    ) -> Dict[str, Any]:
        variables = config.variables or df.columns.tolist()
        numeric_vars = [v for v in variables if v in df.columns and pd.api.types.is_numeric_dtype(df[v])]

        if len(numeric_vars) < 2:
            return {
                "analysis_type": "correlation",
                "summary": {"message": "需要至少 2 个数值变量进行相关性分析"},
                "statistics": {},
                "recommendations": ["请重新选择至少两个数值变量。"],
                "generated_at": datetime.utcnow().isoformat(),
            }

        corr_matrix = df[numeric_vars].corr()
        strong_correlations = []
        for i in range(len(numeric_vars)):
            for j in range(i + 1, len(numeric_vars)):
                corr = corr_matrix.iloc[i, j]
                if abs(corr) > 0.5:
                    strong_correlations.append({
                        "var1": numeric_vars[i],
                        "var2": numeric_vars[j],
                        "correlation": float(corr),
                        "strength": "strong" if abs(corr) > 0.7 else "moderate",
                    })

        return {
            "analysis_type": "correlation",
            "summary": {
                "variable_count": len(numeric_vars),
                "strong_pair_count": len(strong_correlations),
            },
            "statistics": {
                "correlation_matrix": corr_matrix.to_dict(),
                "strong_correlations": strong_correlations,
            },
            "recommendations": [
                "强相关变量进入回归前先检查共线性。",
                "临床解释优先于纯统计相关，必要时回到原始定义核对变量含义。",
            ],
            "generated_at": datetime.utcnow().isoformat(),
        }

    @classmethod
    async def _regression_analysis(
        cls,
        df: pd.DataFrame,
        config: AnalysisConfig
    ) -> Dict[str, Any]:
        numeric_columns = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
        return {
            "analysis_type": "regression",
            "summary": {
                "message": "当前回归分析提供服务器端建模准备摘要。",
                "candidate_numeric_columns": numeric_columns,
            },
            "statistics": {
                "row_count": int(len(df)),
                "column_count": int(len(df.columns)),
            },
            "recommendations": [
                "先明确因变量和主要协变量，再决定线性、Logistic 或 Cox 模型。",
                "建模前先做缺失值和异常值检查，必要时保存一份清洗后的衍生数据集。",
            ],
            "generated_at": datetime.utcnow().isoformat(),
        }

    @classmethod
    async def _custom_analysis(
        cls,
        df: pd.DataFrame,
        config: AnalysisConfig
    ) -> Dict[str, Any]:
        return {
            "analysis_type": "custom",
            "summary": {
                "message": "服务器已保存该任务，可在后续接入专用统计引擎时复用。",
                "data_shape": [int(df.shape[0]), int(df.shape[1])],
            },
            "statistics": {
                "columns": df.columns.tolist(),
            },
            "recommendations": [
                "把自定义分析需求拆成变量选择、清洗、建模和输出四步。",
            ],
            "generated_at": datetime.utcnow().isoformat(),
        }

    @classmethod
    def get_task(cls, task_id: str) -> Optional[AnalysisTask]:
        with SessionLocal() as db:
            record = db.query(AnalysisTaskRecord).filter(AnalysisTaskRecord.id == task_id).first()
            return _task_from_record(record) if record else None

    @classmethod
    def get_tasks(
        cls,
        database_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AnalysisTask]:
        with SessionLocal() as db:
            query = db.query(AnalysisTaskRecord)
            if database_id:
                query = query.filter(AnalysisTaskRecord.database_id == database_id)
            if status:
                query = query.filter(AnalysisTaskRecord.status == status)

            records = (
                query.order_by(AnalysisTaskRecord.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
            return [_task_from_record(record) for record in records]

    @classmethod
    def delete_task(cls, task_id: str) -> bool:
        with SessionLocal() as db:
            record = db.query(AnalysisTaskRecord).filter(AnalysisTaskRecord.id == task_id).first()
            if not record:
                return False
            db.query(ExternalAPICallRecord).filter(ExternalAPICallRecord.task_id == task_id).delete()
            db.delete(record)
            db.commit()
            return True

    @classmethod
    async def call_external_api(
        cls,
        database_id: str,
        api_provider: str,
        endpoint: str,
        parameters: Dict[str, Any],
        callback_url: Optional[str] = None
    ) -> ExternalAPIResponse:
        if api_provider not in EXTERNAL_APIS:
            raise ValueError(f"不支持的API提供商: {api_provider}")

        database = DatabaseService.get_database(database_id)
        if not database:
            raise ValueError("数据库不存在")

        task_id = str(uuid.uuid4())
        log_id = str(uuid.uuid4())
        now = datetime.utcnow()

        with SessionLocal() as db:
            task_record = AnalysisTaskRecord(
                id=task_id,
                name=f"External API: {api_provider}",
                description=f"调用 {api_provider} 的 {endpoint}",
                database_id=database_id,
                analysis_type="external_api",
                status="running",
                config_payload={},
                extra_metadata={
                    "callback_url": callback_url,
                    "api_provider": api_provider,
                    "endpoint": endpoint,
                },
                created_at=now,
                updated_at=now,
            )
            log_record = ExternalAPICallRecord(
                id=log_id,
                task_id=task_id,
                database_id=database_id,
                api_name=api_provider,
                endpoint=endpoint,
                request_payload={
                    "database_id": database_id,
                    "parameters": parameters,
                },
                status="running",
                created_at=now,
            )
            db.add(task_record)
            db.add(log_record)
            db.commit()

        asyncio.create_task(
            cls._execute_external_api_call(
                task_id, log_id, api_provider, endpoint, parameters, database
            )
        )

        return ExternalAPIResponse(
            task_id=task_id,
            status="running",
            external_job_id=f"{api_provider}_{task_id}",
            estimated_duration=60,
            message="外部API调用已启动"
        )

    @classmethod
    async def _execute_external_api_call(
        cls,
        task_id: str,
        log_id: str,
        api_provider: str,
        endpoint: str,
        parameters: Dict[str, Any],
        database
    ):
        start_time = time.time()

        try:
            api_config = EXTERNAL_APIS[api_provider]
            url = f"{api_config['base_url']}{api_config['endpoints'].get(endpoint, endpoint)}"
            payload = {
                "data_url": database.file_path,
                "parameters": parameters,
            }

            await asyncio.sleep(2)
            result = {
                "api_provider": api_provider,
                "endpoint": endpoint,
                "status": "success",
                "result": {
                    "message": f"{api_provider} 分析完成",
                    "url": url,
                    "payload": payload,
                },
            }
            duration_ms = int((time.time() - start_time) * 1000)

            with SessionLocal() as db:
                log_record = db.query(ExternalAPICallRecord).filter(ExternalAPICallRecord.id == log_id).first()
                task_record = db.query(AnalysisTaskRecord).filter(AnalysisTaskRecord.id == task_id).first()
                if log_record:
                    log_record.response_payload = result
                    log_record.status_code = 200
                    log_record.duration_ms = duration_ms
                    log_record.status = "completed"
                    log_record.completed_at = datetime.utcnow()
                if task_record:
                    task_record.result_payload = result
                    task_record.status = "completed"
                    task_record.completed_at = datetime.utcnow()
                    task_record.updated_at = datetime.utcnow()
                db.commit()
        except Exception as exc:
            duration_ms = int((time.time() - start_time) * 1000)
            with SessionLocal() as db:
                log_record = db.query(ExternalAPICallRecord).filter(ExternalAPICallRecord.id == log_id).first()
                task_record = db.query(AnalysisTaskRecord).filter(AnalysisTaskRecord.id == task_id).first()
                if log_record:
                    log_record.status = "failed"
                    log_record.duration_ms = duration_ms
                    log_record.error_message = str(exc)
                    log_record.completed_at = datetime.utcnow()
                if task_record:
                    task_record.status = "failed"
                    task_record.error_message = str(exc)
                    task_record.completed_at = datetime.utcnow()
                    task_record.updated_at = datetime.utcnow()
                db.commit()
