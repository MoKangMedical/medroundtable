"""
研究方案API路由
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional, List
import uuid
from datetime import datetime

from backend.upload_models import (
    ProtocolCreate, ProtocolUpdate, ProtocolResponse, ResearchProtocol
)
from backend.services.protocol_service import ProtocolService

router = APIRouter(prefix="/api/protocols", tags=["研究方案"])


@router.post("/upload", response_model=ProtocolResponse)
async def upload_protocol(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    roundtable_id: Optional[str] = Form(None),
    uploaded_by: Optional[str] = Form(None)
):
    """
    上传研究方案文档
    
    支持格式: PDF, Word(.doc/.docx), Markdown, TXT
    """
    try:
        # 读取文件内容
        content = await file.read()
        
        # 上传协议
        protocol = await ProtocolService.upload_protocol(
            file_content=content,
            filename=file.filename,
            title=title,
            description=description,
            uploaded_by=uploaded_by,
            roundtable_id=roundtable_id
        )
        
        return protocol
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.get("/{protocol_id}", response_model=ProtocolResponse)
async def get_protocol(protocol_id: str):
    """获取研究方案详情"""
    protocol = ProtocolService.get_protocol(protocol_id)
    if not protocol:
        raise HTTPException(status_code=404, detail="研究方案不存在")
    return protocol


@router.get("", response_model=List[ProtocolResponse])
async def list_protocols(
    roundtable_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """
    获取研究方案列表
    
    支持按圆桌会ID和状态过滤
    """
    protocols = ProtocolService.get_protocols(
        roundtable_id=roundtable_id,
        status=status,
        skip=skip,
        limit=limit
    )
    return protocols


@router.put("/{protocol_id}", response_model=ProtocolResponse)
async def update_protocol(
    protocol_id: str,
    update_data: ProtocolUpdate
):
    """更新研究方案信息"""
    protocol = ProtocolService.update_protocol(protocol_id, update_data)
    if not protocol:
        raise HTTPException(status_code=404, detail="研究方案不存在")
    return protocol


@router.delete("/{protocol_id}")
async def delete_protocol(protocol_id: str):
    """删除研究方案"""
    success = ProtocolService.delete_protocol(protocol_id)
    if not success:
        raise HTTPException(status_code=404, detail="研究方案不存在")
    return {"message": "删除成功"}


@router.get("/{protocol_id}/download")
async def download_protocol(protocol_id: str):
    """下载研究方案文件"""
    result = ProtocolService.get_protocol_file(protocol_id)
    if not result:
        raise HTTPException(status_code=404, detail="研究方案或文件不存在")
    
    file_path, file_type = result
    
    # 根据文件类型设置MIME类型
    media_types = {
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'md': 'text/markdown',
        'txt': 'text/plain'
    }
    media_type = media_types.get(file_type, 'application/octet-stream')
    
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=f"protocol_{protocol_id}.{file_type}"
    )


@router.post("/{protocol_id}/analyze")
async def analyze_protocol(protocol_id: str):
    """
    AI分析研究方案
    
    分析研究设计、终点指标、统计方法等
    """
    try:
        result = await ProtocolService.analyze_protocol(protocol_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/{protocol_id}/versions")
async def get_protocol_versions(protocol_id: str):
    """获取研究方案版本历史（待实现）"""
    # TODO: 实现版本控制
    return {"message": "版本控制功能开发中", "protocol_id": protocol_id}
