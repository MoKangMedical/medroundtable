"""
研究方案和数据库管理模型
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, JSON, BigInteger
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

# ============== 研究方案模型 ==============

class ResearchProtocol(BaseModel):
    """研究方案数据模型"""
    id: str
    title: str
    description: Optional[str] = None
    file_path: str
    file_type: str
    file_size: int
    version: int = 1
    status: str = "draft"  # draft, submitted, approved, rejected
    uploaded_by: Optional[str] = None
    roundtable_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None

class ProtocolCreate(BaseModel):
    """创建研究方案请求"""
    title: str
    description: Optional[str] = None
    roundtable_id: Optional[str] = None

class ProtocolUpdate(BaseModel):
    """更新研究方案请求"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ProtocolResponse(BaseModel):
    """研究方案响应"""
    id: str
    title: str
    description: Optional[str]
    file_type: str
    file_size: int
    version: int
    status: str
    uploaded_by: Optional[str]
    roundtable_id: Optional[str]
    created_at: datetime
    updated_at: datetime

# ============== 数据库模型 ==============

class DatabaseColumn(BaseModel):
    """数据库列信息"""
    name: str
    type: str
    nullable: bool = True
    description: Optional[str] = None

class DatabaseSchema(BaseModel):
    """数据库Schema信息"""
    columns: List[DatabaseColumn]
    primary_key: Optional[List[str]] = None
    indexes: Optional[List[Dict[str, Any]]] = None

class ResearchDatabase(BaseModel):
    """研究数据库数据模型"""
    id: str
    name: str
    description: Optional[str] = None
    file_path: str
    file_type: str  # csv, xlsx, sqlite, json
    file_size: int
    schema: Optional[DatabaseSchema] = None
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    uploaded_by: Optional[str] = None
    roundtable_id: Optional[str] = None
    protocol_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None

class DatabaseCreate(BaseModel):
    """创建数据库请求"""
    name: str
    description: Optional[str] = None
    roundtable_id: Optional[str] = None
    protocol_id: Optional[str] = None

class DatabaseUpdate(BaseModel):
    """更新数据库请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DatabaseResponse(BaseModel):
    """数据库响应"""
    id: str
    name: str
    description: Optional[str]
    file_type: str
    file_size: int
    schema: Optional[DatabaseSchema]
    row_count: Optional[int]
    column_count: Optional[int]
    uploaded_by: Optional[str]
    roundtable_id: Optional[str]
    protocol_id: Optional[str]
    created_at: datetime
    updated_at: datetime

class DatabasePreview(BaseModel):
    """数据库预览响应"""
    columns: List[str]
    rows: List[Dict[str, Any]]
    total_rows: int
    preview_rows: int

# ============== 分析任务模型 ==============

class AnalysisConfig(BaseModel):
    """分析配置"""
    variables: Optional[List[str]] = None
    target_variable: Optional[str] = None
    covariates: Optional[List[str]] = None
    group_by: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    include_missing: bool = True
    generate_charts: bool = True
    confidence_level: float = 0.95
    sample_rows: int = 1000
    max_categories: int = 10
    hypothesis: Optional[str] = None

class AnalysisTask(BaseModel):
    """分析任务数据模型"""
    id: str
    name: str
    description: Optional[str] = None
    database_id: str
    analysis_type: str  # descriptive, comparative, correlation, regression, custom
    status: str = "pending"  # pending, running, completed, failed
    config: Optional[AnalysisConfig] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

class AnalysisCreate(BaseModel):
    """创建分析任务请求"""
    name: str
    description: Optional[str] = None
    database_id: str
    analysis_type: str
    config: Optional[AnalysisConfig] = None

class AnalysisResult(BaseModel):
    """分析结果"""
    task_id: str
    status: str
    summary: Optional[Dict[str, Any]] = None
    statistics: Optional[Dict[str, Any]] = None
    charts: Optional[List[Dict[str, Any]]] = None
    tables: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[List[str]] = None
    completed_at: Optional[datetime] = None


class ColumnProfile(BaseModel):
    """单列画像"""
    name: str
    data_type: str
    inferred_role: str
    non_null_count: int
    missing_count: int
    missing_rate: float
    unique_count: int
    sample_values: List[Any] = []
    numeric_summary: Optional[Dict[str, Any]] = None
    categorical_summary: Optional[Dict[str, Any]] = None


class DatabaseProfile(BaseModel):
    """数据库分析画像"""
    database_id: str
    database_name: str
    total_rows: int
    total_columns: int
    numeric_columns: List[str]
    categorical_columns: List[str]
    datetime_columns: List[str]
    recommended_group_by: List[str]
    recommended_targets: List[str]
    missingness_overview: List[Dict[str, Any]]
    column_profiles: List[ColumnProfile]
    generated_at: datetime


class AnalysisSuggestion(BaseModel):
    """建议的分析动作"""
    analysis_type: str
    title: str
    rationale: str
    recommended_variables: List[str] = []
    target_variable: Optional[str] = None
    group_by: Optional[str] = None
    estimated_outputs: List[str] = []


class AnalysisPlanRequest(BaseModel):
    """自动分析规划请求"""
    database_id: str
    objective: str
    clinical_question: str
    research_stage: Optional[str] = None
    preferred_analysis_types: List[str] = []
    required_outputs: List[str] = []
    constraints: List[str] = []


class AnalysisPlanResponse(BaseModel):
    """自动分析规划响应"""
    database_profile: DatabaseProfile
    stella_workflow: Dict[str, Any]
    suggested_analyses: List[AnalysisSuggestion]
    recommended_skills: List[Dict[str, Any]]
    recommended_agents: List[str]
    execution_notes: List[str]

# ============== API调用日志模型 ==============

class APICallLog(BaseModel):
    """API调用日志"""
    id: str
    task_id: Optional[str] = None
    api_name: str
    endpoint: str
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    status_code: Optional[int] = None
    duration_ms: Optional[int] = None
    created_at: datetime

# ============== SQL查询模型 ==============

class SQLQuery(BaseModel):
    """SQL查询请求"""
    sql: str
    params: Optional[Dict[str, Any]] = None
    limit: int = 100
    offset: int = 0

class SQLQueryResult(BaseModel):
    """SQL查询结果"""
    columns: List[str]
    rows: List[Dict[str, Any]]
    total_count: int
    execution_time_ms: int

# ============== 外部API调用模型 ==============

class ExternalAPICall(BaseModel):
    """调用外部API请求"""
    database_id: str
    api_provider: str  # nhanes_analyzer, seer_analyzer, medivisual, clawbio
    endpoint: str
    parameters: Dict[str, Any]
    callback_url: Optional[str] = None

class ExternalAPIResponse(BaseModel):
    """外部API调用响应"""
    task_id: str
    status: str
    external_job_id: Optional[str] = None
    estimated_duration: Optional[int] = None
    message: str


class PublicDatasetSnapshotCreate(BaseModel):
    """将公开数据库查询结果保存到服务器"""
    database: str
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: int = 20
    name: Optional[str] = None
    description: Optional[str] = None
    roundtable_id: Optional[str] = None
    protocol_id: Optional[str] = None
    uploaded_by: Optional[str] = None
