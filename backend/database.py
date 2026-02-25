from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid
import hashlib
import os

# 使用SQLite作为数据库（轻量级，无需额外安装）
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./medroundtable.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    institution = Column(String(255), nullable=True)
    department = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    
    # 关联
    sessions = relationship("SessionHistory", back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
    
    def set_password(self, password: str):
        """设置密码（使用SHA256哈希）"""
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password: str) -> bool:
        """验证密码"""
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()

class SessionHistory(Base):
    """会话历史记录表"""
    __tablename__ = "session_histories"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    session_id = Column(String(36), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    clinical_question = Column(Text, nullable=False)
    status = Column(String(50), default="completed")
    study_type = Column(String(50), nullable=True)
    
    # 存储完整会话数据（JSON格式）
    messages = Column(JSON, default=list)
    study_design = Column(JSON, nullable=True)
    crf_template = Column(JSON, nullable=True)
    analysis_plan = Column(JSON, nullable=True)
    
    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # 标签和收藏
    tags = Column(JSON, default=list)
    is_favorite = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    
    # 关联
    user = relationship("User", back_populates="sessions")

class Feedback(Base):
    """用户反馈表"""
    __tablename__ = "feedbacks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联用户（可选，支持匿名反馈）
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # 反馈内容
    feedback_type = Column(String(50), nullable=False)  # bug, feature, improvement, other
    category = Column(String(50), nullable=True)  # ui, ai_response, export, performance, etc.
    rating = Column(Integer, nullable=True)  # 1-5星评分
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    
    # 上下文信息
    page_url = Column(String(500), nullable=True)
    session_id = Column(String(36), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # 联系信息（匿名反馈时）
    contact_email = Column(String(255), nullable=True)
    
    # 状态
    status = Column(String(50), default="pending")  # pending, processing, resolved, rejected
    admin_response = Column(Text, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    # 关联
    user = relationship("User", back_populates="feedbacks")

class UsageStats(Base):
    """使用统计表"""
    __tablename__ = "usage_stats"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    session_id = Column(String(36), nullable=True)
    
    # 操作类型
    action = Column(String(50), nullable=False)  # create_session, send_message, export, search_literature, etc.
    
    # 详情
    details = Column(JSON, default=dict)
    
    # IP和时间
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# 创建所有表
def init_db():
    """初始化数据库"""
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库初始化完成")

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
