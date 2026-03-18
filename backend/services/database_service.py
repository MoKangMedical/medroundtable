"""
数据库服务层
处理数据库文件的上传、存储、解析和分析
"""
import os
import uuid
import json
import sqlite3
import pandas as pd
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
import io

from backend.upload_models import (
    ResearchDatabase, DatabaseCreate, DatabaseUpdate, DatabaseResponse,
    DatabaseSchema, DatabaseColumn, DatabasePreview, SQLQuery, SQLQueryResult
)

# 上传目录配置
UPLOAD_DIR = Path("/tmp/medroundtable/uploads")
DATABASES_DIR = UPLOAD_DIR / "databases"

# 确保目录存在
DATABASES_DIR.mkdir(parents=True, exist_ok=True)

# 内存存储（生产环境应使用数据库）
databases_db: Dict[str, ResearchDatabase] = {}


class DatabaseService:
    """数据库服务"""
    
    ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls', '.json', '.sqlite', '.db'}
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """获取文件扩展名"""
        return Path(filename).suffix.lower()
    
    @classmethod
    def is_allowed_file(cls, filename: str) -> bool:
        """检查文件类型是否允许"""
        ext = cls.get_file_extension(filename)
        return ext in cls.ALLOWED_EXTENSIONS
    
    @classmethod
    async def upload_database(
        cls,
        file_content: bytes,
        filename: str,
        name: str,
        description: Optional[str] = None,
        uploaded_by: Optional[str] = None,
        roundtable_id: Optional[str] = None,
        protocol_id: Optional[str] = None
    ) -> ResearchDatabase:
        """上传数据库文件"""
        
        # 验证文件类型
        if not cls.is_allowed_file(filename):
            raise ValueError(f"不支持的文件类型。允许的类型: {cls.ALLOWED_EXTENSIONS}")
        
        # 验证文件大小
        if len(file_content) > cls.MAX_FILE_SIZE:
            raise ValueError(f"文件大小超过限制 ({cls.MAX_FILE_SIZE / 1024 / 1024}MB)")
        
        # 生成唯一ID
        database_id = str(uuid.uuid4())
        
        # 生成存储路径
        file_ext = cls.get_file_extension(filename)
        storage_filename = f"{database_id}{file_ext}"
        file_path = DATABASES_DIR / storage_filename
        
        # 保存文件
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # 解析数据schema
        schema = None
        row_count = None
        column_count = None
        
        try:
            schema, row_count, column_count = await cls._parse_schema(file_path, file_ext)
        except Exception as e:
            print(f"解析schema失败: {e}")
        
        # 创建数据库记录
        now = datetime.utcnow()
        database = ResearchDatabase(
            id=database_id,
            name=name,
            description=description,
            file_path=str(file_path),
            file_type=file_ext[1:],
            file_size=len(file_content),
            schema=schema,
            row_count=row_count,
            column_count=column_count,
            uploaded_by=uploaded_by,
            roundtable_id=roundtable_id,
            protocol_id=protocol_id,
            created_at=now,
            updated_at=now,
            metadata={
                "original_filename": filename,
                "upload_timestamp": now.isoformat(),
                "parsed": schema is not None
            }
        )
        
        # 存储到数据库
        databases_db[database_id] = database
        
        return database
    
    @classmethod
    async def _parse_schema(
        cls,
        file_path: Path,
        file_ext: str
    ) -> Tuple[Optional[DatabaseSchema], Optional[int], Optional[int]]:
        """解析数据库schema"""
        
        if file_ext == '.csv':
            return await cls._parse_csv_schema(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            return await cls._parse_excel_schema(file_path)
        elif file_ext == '.json':
            return await cls._parse_json_schema(file_path)
        elif file_ext in ['.sqlite', '.db']:
            return await cls._parse_sqlite_schema(file_path)
        else:
            return None, None, None
    
    @classmethod
    async def _parse_csv_schema(cls, file_path: Path) -> Tuple[DatabaseSchema, int, int]:
        """解析CSV文件schema"""
        df = pd.read_csv(file_path, nrows=1000)
        
        columns = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            columns.append(DatabaseColumn(
                name=str(col),
                type=dtype,
                nullable=df[col].isnull().any(),
                description=None
            ))
        
        # 获取总行数
        row_count = sum(1 for _ in open(file_path)) - 1  # 减去表头
        
        return DatabaseSchema(columns=columns), row_count, len(columns)
    
    @classmethod
    async def _parse_excel_schema(cls, file_path: Path) -> Tuple[DatabaseSchema, int, int]:
        """解析Excel文件schema"""
        df = pd.read_excel(file_path, nrows=1000)
        
        columns = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            columns.append(DatabaseColumn(
                name=str(col),
                type=dtype,
                nullable=df[col].isnull().any(),
                description=None
            ))
        
        # 获取总行数（近似）
        full_df = pd.read_excel(file_path)
        row_count = len(full_df)
        
        return DatabaseSchema(columns=columns), row_count, len(columns)
    
    @classmethod
    async def _parse_json_schema(cls, file_path: Path) -> Tuple[DatabaseSchema, int, int]:
        """解析JSON文件schema"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list) and len(data) > 0:
            # JSON数组格式
            first_item = data[0]
            columns = [
                DatabaseColumn(name=k, type=type(v).__name__, nullable=False)
                for k, v in first_item.items()
            ]
            return DatabaseSchema(columns=columns), len(data), len(columns)
        elif isinstance(data, dict):
            # JSON对象格式
            columns = [
                DatabaseColumn(name=k, type=type(v).__name__, nullable=False)
                for k, v in data.items()
            ]
            return DatabaseSchema(columns=columns), 1, len(columns)
        else:
            return DatabaseSchema(columns=[]), 0, 0
    
    @classmethod
    async def _parse_sqlite_schema(
        cls,
        file_path: Path
    ) -> Tuple[DatabaseSchema, int, int]:
        """解析SQLite文件schema"""
        conn = sqlite3.connect(str(file_path))
        cursor = conn.cursor()
        
        # 获取表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if not tables:
            conn.close()
            return DatabaseSchema(columns=[]), 0, 0
        
        # 使用第一个表
        table_name = tables[0][0]
        
        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()
        
        columns = [
            DatabaseColumn(
                name=col[1],
                type=col[2],
                nullable=not col[3],
                description=None
            )
            for col in columns_info
        ]
        
        # 获取行数
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        
        conn.close()
        
        return DatabaseSchema(columns=columns), row_count, len(columns)
    
    @classmethod
    def get_database(cls, database_id: str) -> Optional[ResearchDatabase]:
        """获取数据库信息"""
        return databases_db.get(database_id)
    
    @classmethod
    def get_databases(
        cls,
        roundtable_id: Optional[str] = None,
        protocol_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ResearchDatabase]:
        """获取数据库列表"""
        databases = list(databases_db.values())
        
        # 过滤
        if roundtable_id:
            databases = [d for d in databases if d.roundtable_id == roundtable_id]
        if protocol_id:
            databases = [d for d in databases if d.protocol_id == protocol_id]
        
        # 排序和分页
        databases.sort(key=lambda x: x.created_at, reverse=True)
        return databases[skip:skip + limit]
    
    @classmethod
    async def get_preview(
        cls,
        database_id: str,
        limit: int = 100
    ) -> Optional[DatabasePreview]:
        """获取数据预览"""
        database = databases_db.get(database_id)
        if not database:
            return None
        
        file_path = Path(database.file_path)
        file_type = database.file_type
        
        try:
            if file_type == 'csv':
                df = pd.read_csv(file_path, nrows=limit)
            elif file_type in ['xlsx', 'xls']:
                df = pd.read_excel(file_path, nrows=limit)
            elif file_type == 'json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    df = pd.DataFrame(data[:limit])
                else:
                    df = pd.DataFrame([data])
            elif file_type in ['sqlite', 'db']:
                conn = sqlite3.connect(str(file_path))
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                table_name = cursor.fetchone()[0]
                df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT {limit}", conn)
                conn.close()
            else:
                return None
            
            # 转换DataFrame为字典列表
            rows = df.head(limit).to_dict('records')
            columns = df.columns.tolist()
            
            # 处理NaN值
            for row in rows:
                for key, value in row.items():
                    if pd.isna(value):
                        row[key] = None
            
            return DatabasePreview(
                columns=columns,
                rows=rows,
                total_rows=database.row_count or 0,
                preview_rows=min(limit, len(rows))
            )
            
        except Exception as e:
            print(f"获取预览失败: {e}")
            return None
    
    @classmethod
    async def execute_sql(
        cls,
        database_id: str,
        query: SQLQuery
    ) -> Optional[SQLQueryResult]:
        """执行SQL查询"""
        database = databases_db.get(database_id)
        if not database:
            return None
        
        file_path = Path(database.file_path)
        file_type = database.file_type
        
        if file_type not in ['sqlite', 'db']:
            raise ValueError("只有SQLite数据库支持SQL查询")
        
        import time
        start_time = time.time()
        
        try:
            conn = sqlite3.connect(str(file_path))
            conn.row_factory = sqlite3.Row
            
            # 执行查询
            cursor = conn.execute(query.sql, query.params or {})
            
            # 获取列名
            columns = [description[0] for description in cursor.description]
            
            # 获取数据
            rows = []
            for row in cursor.fetchall():
                rows.append(dict(row))
            
            # 获取总行数
            count_cursor = conn.execute(f"SELECT COUNT(*) FROM ({query.sql}) as t")
            total_count = count_cursor.fetchone()[0]
            
            conn.close()
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return SQLQueryResult(
                columns=columns,
                rows=rows,
                total_count=total_count,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            raise ValueError(f"SQL执行错误: {str(e)}")
    
    @classmethod
    def delete_database(cls, database_id: str) -> bool:
        """删除数据库"""
        database = databases_db.get(database_id)
        if not database:
            return False
        
        # 删除文件
        try:
            if os.path.exists(database.file_path):
                os.remove(database.file_path)
        except Exception as e:
            print(f"删除文件失败: {e}")
        
        # 从数据库移除
        del databases_db[database_id]
        return True
