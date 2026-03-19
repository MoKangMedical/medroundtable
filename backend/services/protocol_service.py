"""
研究方案服务层
处理研究方案的上传、存储、管理和分析
"""
import os
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from backend.database import ProtocolRecord, SessionLocal
from backend.upload_models import (
    ResearchProtocol, ProtocolCreate, ProtocolUpdate, ProtocolResponse
)

def _resolve_upload_root() -> Path:
    """解析上传根目录，优先环境变量，其次项目内 data/uploads。"""
    configured_path = os.getenv("MRT_UPLOAD_DIR") or os.getenv("MEDROUNDTABLE_UPLOAD_DIR")
    if configured_path:
        return Path(configured_path).expanduser().resolve()
    return Path(__file__).resolve().parents[2] / "data" / "uploads"


UPLOAD_DIR = _resolve_upload_root()
PROTOCOLS_DIR = UPLOAD_DIR / "protocols"
PROTOCOLS_DIR.mkdir(parents=True, exist_ok=True)

def _protocol_from_record(record: ProtocolRecord) -> ResearchProtocol:
    """将 ORM 记录转换为 Pydantic 模型"""
    return ResearchProtocol(
        id=record.id,
        title=record.title,
        description=record.description,
        file_path=record.file_path,
        file_type=record.file_type,
        file_size=record.file_size,
        version=record.version,
        status=record.status,
        uploaded_by=record.uploaded_by,
        roundtable_id=record.roundtable_id,
        created_at=record.created_at,
        updated_at=record.updated_at,
        metadata=record.extra_metadata or {}
    )


class ProtocolService:
    """研究方案服务"""
    
    ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.md', '.txt'}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """获取文件扩展名"""
        return Path(filename).suffix.lower()
    
    @staticmethod
    def is_allowed_file(filename: str) -> bool:
        """检查文件类型是否允许"""
        ext = ProtocolService.get_file_extension(filename)
        return ext in ProtocolService.ALLOWED_EXTENSIONS
    
    @classmethod
    async def upload_protocol(
        cls,
        file_content: bytes,
        filename: str,
        title: str,
        description: Optional[str] = None,
        uploaded_by: Optional[str] = None,
        roundtable_id: Optional[str] = None
    ) -> ResearchProtocol:
        """上传研究方案"""
        
        # 验证文件类型
        if not cls.is_allowed_file(filename):
            raise ValueError(f"不支持的文件类型。允许的类型: {cls.ALLOWED_EXTENSIONS}")
        
        # 验证文件大小
        if len(file_content) > cls.MAX_FILE_SIZE:
            raise ValueError(f"文件大小超过限制 ({cls.MAX_FILE_SIZE / 1024 / 1024}MB)")
        
        # 生成唯一ID
        protocol_id = str(uuid.uuid4())
        
        # 生成存储路径
        file_ext = cls.get_file_extension(filename)
        storage_filename = f"{protocol_id}{file_ext}"
        file_path = PROTOCOLS_DIR / storage_filename
        
        # 保存文件
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        now = datetime.utcnow()
        record = ProtocolRecord(
            id=protocol_id,
            title=title,
            description=description,
            file_path=str(file_path),
            file_type=file_ext[1:],
            file_size=len(file_content),
            version=1,
            status="uploaded",
            uploaded_by=uploaded_by,
            roundtable_id=roundtable_id,
            created_at=now,
            updated_at=now,
            extra_metadata={
                "original_filename": filename,
                "upload_timestamp": now.isoformat()
            }
        )

        with SessionLocal() as db:
            db.add(record)
            db.commit()
            db.refresh(record)

        return _protocol_from_record(record)
    
    @classmethod
    def get_protocol(cls, protocol_id: str) -> Optional[ResearchProtocol]:
        """获取研究方案"""
        with SessionLocal() as db:
            record = db.query(ProtocolRecord).filter(ProtocolRecord.id == protocol_id).first()
            return _protocol_from_record(record) if record else None
    
    @classmethod
    def get_protocols(
        cls,
        roundtable_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ResearchProtocol]:
        """获取研究方案列表"""
        with SessionLocal() as db:
            query = db.query(ProtocolRecord)
            if roundtable_id:
                query = query.filter(ProtocolRecord.roundtable_id == roundtable_id)
            if status:
                query = query.filter(ProtocolRecord.status == status)

            records = (
                query.order_by(ProtocolRecord.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
            return [_protocol_from_record(record) for record in records]
    
    @classmethod
    def update_protocol(
        cls,
        protocol_id: str,
        update_data: ProtocolUpdate
    ) -> Optional[ResearchProtocol]:
        """更新研究方案"""
        with SessionLocal() as db:
            record = db.query(ProtocolRecord).filter(ProtocolRecord.id == protocol_id).first()
            if not record:
                return None

            if update_data.title is not None:
                record.title = update_data.title
            if update_data.description is not None:
                record.description = update_data.description
            if update_data.status is not None:
                record.status = update_data.status
            if update_data.metadata is not None:
                record.extra_metadata = {**(record.extra_metadata or {}), **update_data.metadata}

            record.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(record)
            return _protocol_from_record(record)
    
    @classmethod
    def delete_protocol(cls, protocol_id: str) -> bool:
        """删除研究方案"""
        with SessionLocal() as db:
            record = db.query(ProtocolRecord).filter(ProtocolRecord.id == protocol_id).first()
            if not record:
                return False

            try:
                if os.path.exists(record.file_path):
                    os.remove(record.file_path)
            except Exception as e:
                print(f"删除文件失败: {e}")

            db.delete(record)
            db.commit()
            return True
    
    @classmethod
    def get_protocol_file(cls, protocol_id: str) -> Optional[tuple]:
        """获取研究方案文件"""
        with SessionLocal() as db:
            record = db.query(ProtocolRecord).filter(ProtocolRecord.id == protocol_id).first()
            if not record or not os.path.exists(record.file_path):
                return None

            return (record.file_path, record.file_type)
    
    @classmethod
    async def analyze_protocol(cls, protocol_id: str) -> Dict[str, Any]:
        """AI分析研究方案
        
        这里可以集成AI模型或调用外部API进行分析
        """
        protocol = cls.get_protocol(protocol_id)
        if not protocol:
            raise ValueError("研究方案不存在")
        
        # TODO: 实际实现中，这里应该：
        # 1. 读取文件内容（PDF/Word解析）
        # 2. 调用AI模型进行分析
        # 3. 返回分析结果
        
        # 模拟分析结果
        analysis_result = {
            "protocol_id": protocol_id,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "study_design": {
                "type": "观察性研究",
                "design": "回顾性队列研究",
                "confidence": 0.85
            },
            "endpoints": {
                "primary": "主要终点指标",
                "secondary": ["次要终点1", "次要终点2"],
                "suggested": ["建议添加的终点"]
            },
            "population": {
                "inclusion_criteria": ["纳入标准1", "纳入标准2"],
                "exclusion_criteria": ["排除标准1", "排除标准2"],
                "estimated_sample_size": 300
            },
            "methodology": {
                "statistical_methods": ["生存分析", "Cox回归"],
                "bias_control": ["随机化", "盲法"],
                "quality_score": 8.5
            },
            "recommendations": [
                "建议明确主要终点的测量时间点",
                "建议增加样本量计算依据",
                "建议补充缺失数据处理方案"
            ],
            "compliance": {
                "spirit_checklist": 0.92,
                "ich_gcp": 0.88,
                "ethical_considerations": ["伦理要点1", "伦理要点2"]
            }
        }
        
        # 更新协议元数据
        metadata = protocol.metadata or {}
        updated_protocol = cls.update_protocol(protocol_id, ProtocolUpdate(
            metadata={
                **metadata,
                "last_analysis": analysis_result
            }
        ))
        if not updated_protocol:
            raise ValueError("研究方案更新失败")

        return analysis_result
