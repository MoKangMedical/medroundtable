"""
数据库API路由
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from typing import Optional, List

from backend.upload_models import (
    DatabaseCreate, DatabaseUpdate, DatabaseResponse,
    DatabasePreview, SQLQuery, SQLQueryResult
)
from backend.services.database_service import DatabaseService

router = APIRouter(prefix="/api/databases", tags=["数据库"])


@router.post("/upload", response_model=DatabaseResponse)
async def upload_database(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    roundtable_id: Optional[str] = Form(None),
    protocol_id: Optional[str] = Form(None),
    uploaded_by: Optional[str] = Form(None)
):
    """
    上传数据库文件
    
    支持格式: CSV, Excel(.xlsx/.xls), JSON, SQLite(.sqlite/.db)
    """
    try:
        # 读取文件内容
        content = await file.read()
        
        # 上传数据库
        database = await DatabaseService.upload_database(
            file_content=content,
            filename=file.filename,
            name=name,
            description=description,
            uploaded_by=uploaded_by,
            roundtable_id=roundtable_id,
            protocol_id=protocol_id
        )
        
        return database
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.get("/{database_id}", response_model=DatabaseResponse)
async def get_database(database_id: str):
    """获取数据库详情"""
    database = DatabaseService.get_database(database_id)
    if not database:
        raise HTTPException(status_code=404, detail="数据库不存在")
    return database


@router.get("", response_model=List[DatabaseResponse])
async def list_databases(
    roundtable_id: Optional[str] = None,
    protocol_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """
    获取数据库列表
    
    支持按圆桌会ID和研究方案ID过滤
    """
    databases = DatabaseService.get_databases(
        roundtable_id=roundtable_id,
        protocol_id=protocol_id,
        skip=skip,
        limit=limit
    )
    return databases


@router.get("/{database_id}/preview", response_model=DatabasePreview)
async def preview_database(database_id: str, limit: int = 100):
    """
    获取数据预览
    
    返回前N行数据预览（默认100行）
    """
    preview = await DatabaseService.get_preview(database_id, limit=limit)
    if not preview:
        raise HTTPException(status_code=404, detail="数据库不存在或预览失败")
    return preview


@router.get("/{database_id}/schema")
async def get_database_schema(database_id: str):
    """获取数据库Schema详情"""
    database = DatabaseService.get_database(database_id)
    if not database:
        raise HTTPException(status_code=404, detail="数据库不存在")
    
    if not database.schema:
        raise HTTPException(status_code=400, detail="无法解析数据库schema")
    
    return {
        "database_id": database_id,
        "schema": database.schema,
        "row_count": database.row_count,
        "column_count": database.column_count
    }


@router.post("/{database_id}/query", response_model=SQLQueryResult)
async def query_database(database_id: str, query: SQLQuery):
    """
    执行SQL查询
    
    仅支持SQLite数据库
    """
    try:
        result = await DatabaseService.execute_sql(database_id, query)
        if not result:
            raise HTTPException(status_code=404, detail="数据库不存在")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.delete("/{database_id}")
async def delete_database(database_id: str):
    """删除数据库"""
    success = DatabaseService.delete_database(database_id)
    if not success:
        raise HTTPException(status_code=404, detail="数据库不存在")
    return {"message": "删除成功"}


@router.get("/{database_id}/download")
async def download_database(database_id: str):
    """下载数据库文件"""
    database = DatabaseService.get_database(database_id)
    if not database:
        raise HTTPException(status_code=404, detail="数据库不存在")
    
    import os
    if not os.path.exists(database.file_path):
        raise HTTPException(status_code=404, detail="数据库文件不存在")
    
    # 根据文件类型设置MIME类型
    media_types = {
        'csv': 'text/csv',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'xls': 'application/vnd.ms-excel',
        'json': 'application/json',
        'sqlite': 'application/x-sqlite3',
        'db': 'application/x-sqlite3'
    }
    media_type = media_types.get(database.file_type, 'application/octet-stream')
    
    return FileResponse(
        path=database.file_path,
        media_type=media_type,
        filename=f"{database.name}.{database.file_type}"
    )


@router.get("/{database_id}/stats")
async def get_database_stats(database_id: str):
    """获取数据库统计信息"""
    database = DatabaseService.get_database(database_id)
    if not database:
        raise HTTPException(status_code=404, detail="数据库不存在")
    
    # TODO: 实现更详细的统计分析
    return {
        "database_id": database_id,
        "name": database.name,
        "row_count": database.row_count,
        "column_count": database.column_count,
        "file_size": database.file_size,
        "file_size_formatted": f"{database.file_size / 1024:.2f} KB" if database.file_size < 1024*1024 else f"{database.file_size / (1024*1024):.2f} MB",
        "schema": database.schema
    }
