from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, ForeignKey, JSON, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid
import hashlib
import os

# 使用SQLite作为数据库（轻量级，无需额外安装）
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/medroundtable.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    """用户表 - 支持Second Me OAuth和本地注册"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # OAuth用户可为空
    name = Column(String(100), nullable=False)
    institution = Column(String(255), nullable=True)
    department = Column(String(100), nullable=True)
    title = Column(String(50), nullable=True)  # 职称
    
    # Second Me 集成
    secondme_id = Column(String(100), unique=True, nullable=True, index=True)
    secondme_access_token = Column(Text, nullable=True)
    secondme_refresh_token = Column(Text, nullable=True)
    secondme_token_expires_at = Column(DateTime, nullable=True)
    
    # 用户偏好设置
    preferences = Column(JSON, default=dict)  # 语言、主题、通知设置等
    default_agents = Column(JSON, default=list)  # 默认启用的Agent
    
    # 状态
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_oauth_user = Column(Boolean, default=False)  # 区分OAuth和本地用户
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    last_active_at = Column(DateTime, nullable=True)
    
    # 关联
    sessions = relationship("SessionHistory", back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
    usage_stats = relationship("UsageStats", back_populates="user", cascade="all, delete-orphan")
    saved_documents = relationship("SavedDocument", back_populates="user", cascade="all, delete-orphan")
    
    def set_password(self, password: str):
        """设置密码（使用SHA256哈希）"""
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password: str) -> bool:
        """验证密码"""
        if not self.password_hash:
            return False
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
    
    def to_dict(self):
        """转换为字典（用于API响应）"""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "institution": self.institution,
            "department": self.department,
            "title": self.title,
            "is_oauth_user": self.is_oauth_user,
            "preferences": self.preferences,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None
        }

class SessionHistory(Base):
    """圆桌讨论会话历史 - 完整保存用户所有分析数据"""
    __tablename__ = "session_histories"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    session_id = Column(String(36), unique=True, nullable=False, index=True)
    
    # 基本信息
    title = Column(String(500), nullable=False)
    clinical_question = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    
    # 状态管理
    status = Column(String(50), default="active")  # active, paused, completed, archived
    progress = Column(Integer, default=0)  # 进度百分比
    current_stage = Column(String(50), nullable=True)  # 当前阶段
    
    # 研究类型和元数据
    study_type = Column(String(50), nullable=True)  # RCT, cohort, case-control, etc.
    specialty = Column(String(100), nullable=True)  # 专科领域
    tags = Column(JSON, default=list)
    
    # ========== 核心数据存储 ==========
    
    # 1. 完整消息历史（包含所有Agent对话）
    messages = Column(JSON, default=list)
    # 格式: [{"role": "user/agent", "agent_id": "xxx", "content": "...", "timestamp": "...", "stage": "..."}]
    
    # 2. 临床问题分析
    problem_analysis = Column(JSON, nullable=True)
    # 包含: 问题分解、关键词、PICO要素、初步评估
    
    # 3. 文献检索结果
    literature_review = Column(JSON, nullable=True)
    # 包含: 检索策略、检索结果、文献列表、综述摘要
    
    # 4. 研究设计方案
    study_design = Column(JSON, nullable=True)
    # 包含: 研究类型、设计框架、纳入排除标准、样本量计算、时间线
    
    # 5. CRF表单设计
    crf_template = Column(JSON, nullable=True)
    # 包含: CRF结构、变量定义、表单字段、验证规则
    
    # 6. 统计分析计划
    analysis_plan = Column(JSON, nullable=True)
    # 包含: 统计方法、假设检验、图表计划、软件代码
    
    # 7. 数据收集计划
    data_collection_plan = Column(JSON, nullable=True)
    # 包含: 采集流程、SOP、质控措施、随访计划
    
    # 8. 结果和讨论
    results_discussion = Column(JSON, nullable=True)
    # 包含: 结果摘要、统计解释、临床意义、局限性
    
    # 9. 生成的文档列表
    generated_documents = Column(JSON, default=list)
    # 包含: [{"type": "protocol", "name": "...", "url": "...", "created_at": "..."}]
    
    # 10. 用户反馈和修改历史
    revision_history = Column(JSON, default=list)
    # 包含: 每次修改的记录、用户反馈、版本对比
    
    # 11. 导出历史
    export_history = Column(JSON, default=list)
    # 包含: 导出记录、格式、时间
    
    # ========== 协作功能 ==========
    
    # 协作者（支持多用户协作）
    collaborators = Column(JSON, default=list)
    # 格式: [{"user_id": "...", "role": "viewer/editor", "added_at": "..."}]
    
    # 分享设置
    is_shared = Column(Boolean, default=False)
    share_link = Column(String(100), nullable=True, unique=True)
    share_expires_at = Column(DateTime, nullable=True)
    
    # ========== 元数据 ==========
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    last_accessed_at = Column(DateTime, nullable=True)
    
    # 收藏和归档
    is_favorite = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    
    # 关联
    user = relationship("User", back_populates="sessions")
    
    def to_dict(self, include_full_data=False):
        """转换为字典"""
        data = {
            "id": self.id,
            "session_id": self.session_id,
            "title": self.title,
            "clinical_question": self.clinical_question,
            "description": self.description,
            "status": self.status,
            "progress": self.progress,
            "current_stage": self.current_stage,
            "study_type": self.study_type,
            "specialty": self.specialty,
            "tags": self.tags,
            "is_favorite": self.is_favorite,
            "is_shared": self.is_shared,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
        
        if include_full_data:
            data.update({
                "messages": self.messages,
                "problem_analysis": self.problem_analysis,
                "literature_review": self.literature_review,
                "study_design": self.study_design,
                "crf_template": self.crf_template,
                "analysis_plan": self.analysis_plan,
                "data_collection_plan": self.data_collection_plan,
                "results_discussion": self.results_discussion,
                "generated_documents": self.generated_documents,
                "revision_history": self.revision_history,
            })
        
        return data

class SavedDocument(Base):
    """保存的文档 - 支持各种导出格式"""
    __tablename__ = "saved_documents"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    session_id = Column(String(36), ForeignKey("session_histories.session_id"), nullable=True)
    
    # 文档信息
    document_type = Column(String(50), nullable=False)  # protocol, crf, analysis_plan, manuscript, etc.
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    
    # 文件存储
    file_path = Column(String(1000), nullable=True)  # 本地存储路径
    file_url = Column(String(1000), nullable=True)   # 云存储URL
    file_size = Column(Integer, nullable=True)
    file_format = Column(String(20), nullable=True)  # pdf, docx, xlsx, json, etc.
    
    # 内容（小文件可直接存储）
    content = Column(Text, nullable=True)
    content_json = Column(JSON, nullable=True)
    
    # 版本控制
    version = Column(Integer, default=1)
    parent_version_id = Column(String(36), nullable=True)  # 上一个版本
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    user = relationship("User", back_populates="saved_documents")

class Feedback(Base):
    """用户反馈表"""
    __tablename__ = "feedbacks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    feedback_type = Column(String(50), nullable=False)
    category = Column(String(50), nullable=True)
    rating = Column(Integer, nullable=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    
    page_url = Column(String(500), nullable=True)
    session_id = Column(String(36), nullable=True)
    user_agent = Column(String(500), nullable=True)
    contact_email = Column(String(255), nullable=True)
    
    status = Column(String(50), default="pending")
    admin_response = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="feedbacks")

class UsageStats(Base):
    """使用统计表 - 详细记录用户行为"""
    __tablename__ = "usage_stats"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    session_id = Column(String(36), nullable=True)
    
    # 操作类型
    action = Column(String(50), nullable=False)
    # create_session, send_message, agent_response, export_document, 
    # search_literature, save_draft, share_session, etc.
    
    # 详细信息
    details = Column(JSON, default=dict)
    # 包含: agent_id, message_length, response_time, document_type, etc.
    
    # 性能指标
    response_time_ms = Column(Integer, nullable=True)  # 响应时间（毫秒）
    tokens_used = Column(Integer, nullable=True)  # 使用的token数
    
    # IP和设备信息
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="usage_stats")

class DataBackup(Base):
    """数据备份记录"""
    __tablename__ = "data_backups"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    backup_type = Column(String(50), nullable=False)  # auto, manual, scheduled
    backup_path = Column(String(1000), nullable=False)
    file_size = Column(Integer, nullable=True)
    checksum = Column(String(64), nullable=True)  # SHA256校验
    
    # 备份内容统计
    user_count = Column(Integer, default=0)
    session_count = Column(Integer, default=0)
    document_count = Column(Integer, default=0)
    
    # 状态
    status = Column(String(50), default="running")  # running, completed, failed
    error_message = Column(Text, nullable=True)
    
    # 时间戳
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "backup_type": self.backup_type,
            "backup_path": self.backup_path,
            "file_size": self.file_size,
            "status": self.status,
            "user_count": self.user_count,
            "session_count": self.session_count,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

# 创建所有表
def init_db():
    """初始化数据库"""
    # 确保数据目录存在
    db_path = os.path.dirname(DATABASE_URL.replace("sqlite:///", ""))
    if db_path and not os.path.exists(db_path):
        os.makedirs(db_path, exist_ok=True)
        print(f"✅ 创建数据目录: {db_path}")
    
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库初始化完成")

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 数据导出/导入功能
def export_user_data(user_id: str, db) -> dict:
    """导出用户的所有数据"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    sessions = db.query(SessionHistory).filter(
        SessionHistory.user_id == user_id,
        SessionHistory.is_deleted == False
    ).all()
    
    documents = db.query(SavedDocument).filter(
        SavedDocument.user_id == user_id
    ).all()
    
    return {
        "user": user.to_dict(),
        "sessions": [s.to_dict(include_full_data=True) for s in sessions],
        "documents": [{"id": d.id, "title": d.title, "type": d.document_type} for d in documents],
        "export_time": datetime.utcnow().isoformat(),
        "version": "1.0"
    }
