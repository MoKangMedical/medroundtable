"""
数据分析服务层
处理数据分析任务和外部API调用
"""
import os
import uuid
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
import pandas as pd
import numpy as np

from backend.models.upload_models import (
    AnalysisTask, AnalysisCreate, AnalysisConfig, AnalysisResult,
    ExternalAPICall, ExternalAPIResponse, APICallLog
)
from backend.services.database_service import DatabaseService

# 内存存储（生产环境应使用数据库）
analysis_tasks_db: Dict[str, AnalysisTask] = {}
api_logs_db: Dict[str, APICallLog] = {}

# 外部API配置
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
        """创建分析任务"""
        
        # 验证数据库存在
        database = DatabaseService.get_database(database_id)
        if not database:
            raise ValueError("数据库不存在")
        
        # 创建任务
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
            created_at=now
        )
        
        analysis_tasks_db[task_id] = task
        
        # 异步执行分析
        asyncio.create_task(cls._execute_analysis(task_id))
        
        return task
    
    @classmethod
    async def _execute_analysis(cls, task_id: str):
        """执行分析任务"""
        task = analysis_tasks_db.get(task_id)
        if not task:
            return
        
        # 更新状态为运行中
        task.status = "running"
        analysis_tasks_db[task_id] = task
        
        try:
            # 获取数据库
            database = DatabaseService.get_database(task.database_id)
            if not database:
                raise ValueError("数据库不存在")
            
            # 加载数据
            df = await cls._load_dataframe(database)
            if df is None:
                raise ValueError("无法加载数据")
            
            # 根据分析类型执行分析
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
            
            # 更新任务结果
            task.result = result
            task.status = "completed"
            task.completed_at = datetime.utcnow()
            
        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
        
        analysis_tasks_db[task_id] = task
    
    @classmethod
    async def _load_dataframe(cls, database) -> Optional[pd.DataFrame]:
        """加载数据到DataFrame"""
        file_path = Path(database.file_path)
        file_type = database.file_type
        
        try:
            if file_type == 'csv':
                return pd.read_csv(file_path)
            elif file_type in ['xlsx', 'xls']:
                return pd.read_excel(file_path)
            elif file_type == 'json':
                import json
                with open(file_path, 'r') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    return pd.DataFrame(data)
                else:
                    return pd.DataFrame([data])
            elif file_type in ['sqlite', 'db']:
                import sqlite3
                conn = sqlite3.connect(str(file_path))
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                table_name = cursor.fetchone()[0]
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                conn.close()
                return df
            else:
                return None
        except Exception as e:
            print(f"加载数据失败: {e}")
            return None
    
    @classmethod
    async def _descriptive_analysis(
        cls,
        df: pd.DataFrame,
        config: AnalysisConfig
    ) -> Dict[str, Any]:
        """描述性统计分析"""
        
        # 选择变量
        variables = config.variables or df.columns.tolist()
        
        # 数值变量统计
        numeric_stats = {}
        for col in variables:
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
        
        # 分类变量统计
        categorical_stats = {}
        for col in variables:
            if df[col].dtype == 'object':
                value_counts = df[col].value_counts().head(10)
                categorical_stats[col] = {
                    "unique_count": df[col].nunique(),
                    "top_values": value_counts.to_dict()
                }
        
        return {
            "analysis_type": "descriptive",
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "numeric_summary": numeric_stats,
            "categorical_summary": categorical_stats,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    @classmethod
    async def _comparative_analysis(
        cls,
        df: pd.DataFrame,
        config: AnalysisConfig
    ) -> Dict[str, Any]:
        """比较分析"""
        group_by = config.group_by
        variables = config.variables
        
        if not group_by or group_by not in df.columns:
            return {"error": "需要提供分组变量"}
        
        if not variables:
            variables = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
        
        comparison_results = {}
        for var in variables:
            if pd.api.types.is_numeric_dtype(df[var]):
                group_stats = df.groupby(group_by)[var].agg([
                    'count', 'mean', 'std', 'min', 'max'
                ]).to_dict()
                comparison_results[var] = group_stats
        
        return {
            "analysis_type": "comparative",
            "group_by": group_by,
            "variables": variables,
            "group_comparison": comparison_results,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    @classmethod
    async def _correlation_analysis(
        cls,
        df: pd.DataFrame,
        config: AnalysisConfig
    ) -> Dict[str, Any]:
        """相关性分析"""
        variables = config.variables or df.columns.tolist()
        
        # 选择数值变量
        numeric_vars = [v for v in variables if pd.api.types.is_numeric_dtype(df[v])]
        
        if len(numeric_vars) < 2:
            return {"error": "需要至少2个数值变量进行相关性分析"}
        
        # 计算相关系数矩阵
        corr_matrix = df[numeric_vars].corr()
        
        # 找出强相关变量对
        strong_correlations = []
        for i in range(len(numeric_vars)):
            for j in range(i+1, len(numeric_vars)):
                corr = corr_matrix.iloc[i, j]
                if abs(corr) > 0.5:  # 相关性阈值
                    strong_correlations.append({
                        "var1": numeric_vars[i],
                        "var2": numeric_vars[j],
                        "correlation": float(corr),
                        "strength": "strong" if abs(corr) > 0.7 else "moderate"
                    })
        
        return {
            "analysis_type": "correlation",
            "variables": numeric_vars,
            "correlation_matrix": corr_matrix.to_dict(),
            "strong_correlations": strong_correlations,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    @classmethod
    async def _regression_analysis(
        cls,
        df: pd.DataFrame,
        config: AnalysisConfig
    ) -> Dict[str, Any]:
        """回归分析"""
        # 简化的回归分析实现
        return {
            "analysis_type": "regression",
            "message": "回归分析功能开发中",
            "generated_at": datetime.utcnow().isoformat()
        }
    
    @classmethod
    async def _custom_analysis(
        cls,
        df: pd.DataFrame,
        config: AnalysisConfig
    ) -> Dict[str, Any]:
        """自定义分析"""
        return {
            "analysis_type": "custom",
            "message": "自定义分析",
            "data_shape": df.shape,
            "columns": df.columns.tolist(),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    @classmethod
    def get_task(cls, task_id: str) -> Optional[AnalysisTask]:
        """获取分析任务"""
        return analysis_tasks_db.get(task_id)
    
    @classmethod
    def get_tasks(
        cls,
        database_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AnalysisTask]:
        """获取分析任务列表"""
        tasks = list(analysis_tasks_db.values())
        
        if database_id:
            tasks = [t for t in tasks if t.database_id == database_id]
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        tasks.sort(key=lambda x: x.created_at, reverse=True)
        return tasks[skip:skip + limit]
    
    @classmethod
    async def call_external_api(
        cls,
        database_id: str,
        api_provider: str,
        endpoint: str,
        parameters: Dict[str, Any],
        callback_url: Optional[str] = None
    ) -> ExternalAPIResponse:
        """调用外部API进行分析"""
        
        # 验证API提供商
        if api_provider not in EXTERNAL_APIS:
            raise ValueError(f"不支持的API提供商: {api_provider}")
        
        # 验证数据库存在
        database = DatabaseService.get_database(database_id)
        if not database:
            raise ValueError("数据库不存在")
        
        # 创建任务
        task_id = str(uuid.uuid4())
        
        # 记录API调用
        log_id = str(uuid.uuid4())
        api_log = APICallLog(
            id=log_id,
            task_id=task_id,
            api_name=api_provider,
            endpoint=endpoint,
            request_data={
                "database_id": database_id,
                "parameters": parameters
            },
            created_at=datetime.utcnow()
        )
        api_logs_db[log_id] = api_log
        
        # 创建分析任务
        task = AnalysisTask(
            id=task_id,
            name=f"External API: {api_provider}",
            description=f"调用 {api_provider} 的 {endpoint}",
            database_id=database_id,
            analysis_type="external_api",
            status="running",
            config=AnalysisConfig(),
            created_at=datetime.utcnow()
        )
        analysis_tasks_db[task_id] = task
        
        # 异步调用外部API
        asyncio.create_task(cls._execute_external_api_call(
            task_id, log_id, api_provider, endpoint, parameters, database
        ))
        
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
        """执行外部API调用"""
        import aiohttp
        import time
        
        task = analysis_tasks_db.get(task_id)
        api_log = api_logs_db.get(log_id)
        
        if not task or not api_log:
            return
        
        start_time = time.time()
        
        try:
            api_config = EXTERNAL_APIS[api_provider]
            url = f"{api_config['base_url']}{api_config['endpoints'].get(endpoint, endpoint)}"
            
            # 准备请求数据
            payload = {
                "data_url": database.file_path,  # 实际实现中应该是可访问的URL
                "parameters": parameters
            }
            
            # 调用API（这里简化处理，实际需要实现）
            # async with aiohttp.ClientSession() as session:
            #     async with session.post(url, json=payload) as response:
            #         result = await response.json()
            
            # 模拟API调用成功
            await asyncio.sleep(2)  # 模拟延迟
            
            result = {
                "api_provider": api_provider,
                "endpoint": endpoint,
                "status": "success",
                "result": {
                    "message": f"{api_provider} 分析完成",
                    "data_processed": database.row_count,
                    "analysis_summary": "分析结果摘要"
                }
            }
            
            # 更新任务
            task.result = result
            task.status = "completed"
            task.completed_at = datetime.utcnow()
            
            # 更新日志
            api_log.response_data = result
            api_log.status_code = 200
            api_log.duration_ms = int((time.time() - start_time) * 1000)
            
        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            
            api_log.response_data = {"error": str(e)}
            api_log.status_code = 500
            api_log.duration_ms = int((time.time() - start_time) * 1000)
        
        analysis_tasks_db[task_id] = task
        api_logs_db[log_id] = api_log
