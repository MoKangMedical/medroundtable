"""Normalize local analysis output into MedRoundTable result schema 1.1."""
from datetime import datetime, timezone
from typing import Any, Dict, Iterable
import uuid

DENIED_KEYS = {
    "raw_data", "raw_rows", "file_content", "ollama_context", "prompt", "messages",
    "patient_id", "subject_id", "medical_record_number",
}


def _clean(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _clean(item) for key, item in value.items() if key.lower() not in DENIED_KEYS}
    if isinstance(value, list):
        return [_clean(item) for item in value]
    return value


def _list(value: Any) -> list:
    return value if isinstance(value, list) else []


def normalize_result(local_result: Dict[str, Any], *, dataset_id: str, job_id: str) -> Dict[str, Any]:
    """Return the public aggregate-only envelope consumed by the observatory."""
    cleaned = _clean(local_result or {})
    summary = cleaned.get("summary") or {
        "row_count": cleaned.get("row_count", cleaned.get("total_rows", 0)),
        "included": cleaned.get("included", cleaned.get("n", 0)),
        "variable_count": cleaned.get("variable_count", cleaned.get("columns", 0)),
        "association_count": cleaned.get("association_count", cleaned.get("significant_count", 0)),
        "max_effect": cleaned.get("max_effect"),
        "evidence_score": cleaned.get("evidence_score"),
    }
    tables = cleaned.get("tables") or {}
    charts = cleaned.get("charts") or {}
    if "associations" not in tables:
        tables["associations"] = _list(cleaned.get("associations") or cleaned.get("results"))
    return {
        "schema_version": "medroundtable.analysis-result/1.1",
        "job_id": job_id,
        "dataset_id": dataset_id,
        "summary": summary,
        "timeline": _list(cleaned.get("timeline")),
        "agent_notes": _list(cleaned.get("agent_notes")),
        "charts": {
            "forest": _list(charts.get("forest") or cleaned.get("forest")),
            "km": charts.get("km") or cleaned.get("km") or {"groups": [], "log_rank_p": None},
            "missingness": _list(charts.get("missingness") or cleaned.get("missingness")),
        },
        "tables": {
            "baseline": tables.get("baseline") or {"columns": [], "rows": [], "footnotes": []},
            "associations": _list(tables.get("associations")),
        },
        "interpretation": cleaned.get("interpretation", ""),
        "review_items": _list(cleaned.get("review_items")),
        "evidence_score": cleaned.get("evidence_score") or summary.get("evidence_score"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def synthetic_result(dataset_id: str, job_id: str) -> Dict[str, Any]:
    """Deterministic aggregate-only fixture for production smoke tests."""
    local = {
        "summary": {"row_count": 2400, "included": 2280, "variable_count": 18, "association_count": 4, "max_effect": 1.48, "evidence_score": "98%"},
        "timeline": [
            {"timestamp": "00:00", "stage": "validation", "title": "方案签名校验通过", "detail": "analysis-result/1.1"},
            {"timestamp": "00:01", "stage": "analysis", "title": "合成队列分析完成", "detail": "Cox + Kaplan–Meier + baseline"},
            {"timestamp": "00:02", "stage": "report", "title": "结构化结果与论文草稿生成", "detail": "仅含聚合统计"},
        ],
        "agent_notes": [
            {"code": "ST", "name": "统计学家", "content": "比例风险假设在合成数据中通过检验。"},
            {"code": "CV", "name": "论断校验器", "content": "所有展示数字均可追溯至本次合成任务。"},
        ],
        "charts": {
            "forest": [
                {"label": "年龄 ≥65", "effect": 1.48, "ci_low": 1.19, "ci_high": 1.84, "p_value": 0.001},
                {"label": "吸烟", "effect": 1.31, "ci_low": 1.08, "ci_high": 1.59, "p_value": 0.006},
                {"label": "治疗组", "effect": 0.72, "ci_low": 0.58, "ci_high": 0.89, "p_value": 0.003},
            ],
            "km": {"log_rank_p": 0.012, "groups": [
                {"label": "治疗组", "points": [{"time": 0, "survival": 1.0, "at_risk": 1140}, {"time": 6, "survival": .94, "at_risk": 1032}, {"time": 12, "survival": .87, "at_risk": 891}, {"time": 18, "survival": .81, "at_risk": 702}, {"time": 24, "survival": .76, "at_risk": 515}]},
                {"label": "对照组", "points": [{"time": 0, "survival": 1.0, "at_risk": 1140}, {"time": 6, "survival": .91, "at_risk": 995}, {"time": 12, "survival": .80, "at_risk": 806}, {"time": 18, "survival": .70, "at_risk": 611}, {"time": 24, "survival": .63, "at_risk": 422}]},
            ]},
            "missingness": [{"variable": "age", "missing_rate": 0.0}, {"variable": "smoking", "missing_rate": 3.2}, {"variable": "bmi", "missing_rate": 6.8}, {"variable": "stage", "missing_rate": 1.1}],
        },
        "tables": {
            "baseline": {"columns": ["变量", "总体 (n=2280)", "治疗组 (n=1140)", "对照组 (n=1140)", "SMD"], "rows": [["年龄，岁", "63.1 ± 9.8", "62.9 ± 9.7", "63.3 ± 9.9", "0.04"], ["女性", "1,094 (48.0%)", "552 (48.4%)", "542 (47.5%)", "0.02"], ["吸烟", "612 (26.8%)", "298 (26.1%)", "314 (27.5%)", "0.03"]], "footnotes": ["连续变量为均值 ± 标准差；分类变量为 n (%)。", "全部数据为合成验收数据。"]},
            "associations": [
                {"feature": "年龄 ≥65", "outcome": "主要事件", "effect": 1.48, "ci": "1.19–1.84", "p_value": "0.001", "fdr": "0.004", "status": "稳健"},
                {"feature": "吸烟", "outcome": "主要事件", "effect": 1.31, "ci": "1.08–1.59", "p_value": "0.006", "fdr": "0.018", "status": "稳健"},
                {"feature": "治疗组", "outcome": "主要事件", "effect": 0.72, "ci": "0.58–0.89", "p_value": "0.003", "fdr": "0.011", "status": "保护"},
            ],
        },
        "interpretation": "在合成数据中，治疗组的事件风险较低，Kaplan–Meier 曲线分离且 log-rank P=0.012。该结果只用于验证系统链路。",
        "review_items": ["确认正式数据中的时间零点定义。", "真实研究需重新检验比例风险假设。", "禁止将合成结果用于临床判断。"],
    }
    return normalize_result(local, dataset_id=dataset_id, job_id=job_id)


def synthetic_paper() -> str:
    return """# MedRoundTable 合成队列全链路验证报告

## 摘要
本研究使用 2,400 条合成记录验证研究方案签名、云端任务队列、Windows connector 执行、结构化图表和论文草稿回传。最终纳入 2,280 条记录，系统成功生成基线表、森林图及 Kaplan–Meier 曲线。

## 结果
合成治疗组与对照组的 Kaplan–Meier 曲线出现分离（log-rank P=0.012）。治疗组风险比为 0.72（95% CI 0.58–0.89）。

## 结论
签名、执行、结果和论文回传链路通过。所有数字均为合成验收数据，不构成医学或临床结论。"""
