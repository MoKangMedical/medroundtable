from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import uuid
import jwt
import os

from backend.database import get_db, User, SessionHistory, Feedback, UsageStats

router = APIRouter(prefix="/api/v1/user", tags=["用户系统"])
security = HTTPBearer()

# JWT配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

# ============ 数据模型 ============

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    institution: Optional[str] = None
    department: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    institution: Optional[str]
    department: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class SessionHistoryCreate(BaseModel):
    session_id: str
    title: str
    clinical_question: str
    study_type: Optional[str] = None
    messages: List[dict] = []
    study_design: Optional[dict] = None
    crf_template: Optional[dict] = None
    analysis_plan: Optional[dict] = None

class SessionHistoryResponse(BaseModel):
    id: str
    session_id: str
    title: str
    clinical_question: str
    status: str
    study_type: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_favorite: bool
    tags: List[str]
    
    class Config:
        from_attributes = True

class FeedbackCreate(BaseModel):
    feedback_type: str  # bug, feature, improvement, other
    category: Optional[str] = None
    rating: Optional[int] = None  # 1-5
    title: str
    content: str
    page_url: Optional[str] = None
    session_id: Optional[str] = None
    contact_email: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: str
    feedback_type: str
    category: Optional[str]
    rating: Optional[int]
    title: str
    content: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============ 辅助函数 ============

def create_access_token(user_id: str) -> str:
    """创建JWT令牌"""
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow().timestamp() + 86400 * 7  # 7天过期
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """验证JWT令牌并获取当前用户"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """可选的用户验证（用于匿名操作）"""
    if not credentials:
        return None
    try:
        return get_current_user(credentials, db)
    except:
        return None

# ============ 用户认证API ============

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查邮箱是否已存在
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 创建新用户
    user = User(
        id=str(uuid.uuid4()),
        email=user_data.email,
        name=user_data.name,
        institution=user_data.institution,
        department=user_data.department
    )
    user.set_password(user_data.password)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 创建JWT令牌
    token = create_access_token(user.id)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not user.check_password(credentials.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # 更新最后登录时间
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # 创建JWT令牌
    token = create_access_token(user.id)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_me(
    name: Optional[str] = None,
    institution: Optional[str] = None,
    department: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户信息"""
    if name:
        current_user.name = name
    if institution:
        current_user.institution = institution
    if department:
        current_user.department = department
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    if not current_user.check_password(old_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    
    current_user.set_password(new_password)
    db.commit()
    return {"message": "Password updated successfully"}

# ============ 历史记录API ============

@router.get("/history", response_model=List[SessionHistoryResponse])
async def get_history(
    page: int = 1,
    per_page: int = 10,
    favorites_only: bool = False,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的历史记录列表"""
    query = db.query(SessionHistory).filter(
        SessionHistory.user_id == current_user.id,
        SessionHistory.is_deleted == False
    )
    
    if favorites_only:
        query = query.filter(SessionHistory.is_favorite == True)
    
    if search:
        query = query.filter(
            SessionHistory.title.contains(search) | 
            SessionHistory.clinical_question.contains(search)
        )
    
    # 按时间倒序
    query = query.order_by(SessionHistory.updated_at.desc())
    
    # 分页
    total = query.count()
    histories = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return histories

@router.get("/history/{session_id}")
async def get_history_detail(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个历史记录的详细信息"""
    history = db.query(SessionHistory).filter(
        SessionHistory.user_id == current_user.id,
        SessionHistory.session_id == session_id
    ).first()
    
    if not history:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "id": history.id,
        "session_id": history.session_id,
        "title": history.title,
        "clinical_question": history.clinical_question,
        "status": history.status,
        "study_type": history.study_type,
        "messages": history.messages,
        "study_design": history.study_design,
        "crf_template": history.crf_template,
        "analysis_plan": history.analysis_plan,
        "tags": history.tags,
        "is_favorite": history.is_favorite,
        "created_at": history.created_at,
        "updated_at": history.updated_at,
        "completed_at": history.completed_at
    }

@router.post("/history")
async def save_history(
    data: SessionHistoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """保存会话到历史记录"""
    # 检查是否已存在
    existing = db.query(SessionHistory).filter(
        SessionHistory.user_id == current_user.id,
        SessionHistory.session_id == data.session_id
    ).first()
    
    if existing:
        # 更新现有记录
        existing.title = data.title
        existing.clinical_question = data.clinical_question
        existing.study_type = data.study_type
        existing.messages = data.messages
        existing.study_design = data.study_design
        existing.crf_template = data.crf_template
        existing.analysis_plan = data.analysis_plan
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return {"message": "History updated", "id": existing.id}
    else:
        # 创建新记录
        history = SessionHistory(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            session_id=data.session_id,
            title=data.title,
            clinical_question=data.clinical_question,
            study_type=data.study_type,
            messages=data.messages,
            study_design=data.study_design,
            crf_template=data.crf_template,
            analysis_plan=data.analysis_plan
        )
        db.add(history)
        db.commit()
        db.refresh(history)
        return {"message": "History saved", "id": history.id}

@router.put("/history/{session_id}/favorite")
async def toggle_favorite(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """切换收藏状态"""
    history = db.query(SessionHistory).filter(
        SessionHistory.user_id == current_user.id,
        SessionHistory.session_id == session_id
    ).first()
    
    if not history:
        raise HTTPException(status_code=404, detail="Session not found")
    
    history.is_favorite = not history.is_favorite
    db.commit()
    
    return {"is_favorite": history.is_favorite}

@router.put("/history/{session_id}/tags")
async def update_tags(
    session_id: str,
    tags: List[str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新标签"""
    history = db.query(SessionHistory).filter(
        SessionHistory.user_id == current_user.id,
        SessionHistory.session_id == session_id
    ).first()
    
    if not history:
        raise HTTPException(status_code=404, detail="Session not found")
    
    history.tags = tags
    db.commit()
    
    return {"tags": history.tags}

@router.delete("/history/{session_id}")
async def delete_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除历史记录（软删除）"""
    history = db.query(SessionHistory).filter(
        SessionHistory.user_id == current_user.id,
        SessionHistory.session_id == session_id
    ).first()
    
    if not history:
        raise HTTPException(status_code=404, detail="Session not found")
    
    history.is_deleted = True
    db.commit()
    
    return {"message": "History deleted"}

# ============ 反馈API ============

@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    data: FeedbackCreate,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """提交反馈（支持匿名）"""
    feedback = Feedback(
        id=str(uuid.uuid4()),
        user_id=current_user.id if current_user else None,
        feedback_type=data.feedback_type,
        category=data.category,
        rating=data.rating,
        title=data.title,
        content=data.content,
        page_url=data.page_url,
        session_id=data.session_id,
        contact_email=data.contact_email if not current_user else current_user.email
    )
    
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    return feedback

@router.get("/my-feedback", response_model=List[FeedbackResponse])
async def get_my_feedback(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的反馈列表"""
    feedbacks = db.query(Feedback).filter(
        Feedback.user_id == current_user.id
    ).order_by(Feedback.created_at.desc()).all()
    
    return feedbacks

# ============ 统计API ============

@router.get("/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户使用统计"""
    total_sessions = db.query(SessionHistory).filter(
        SessionHistory.user_id == current_user.id,
        SessionHistory.is_deleted == False
    ).count()
    
    favorite_sessions = db.query(SessionHistory).filter(
        SessionHistory.user_id == current_user.id,
        SessionHistory.is_favorite == True,
        SessionHistory.is_deleted == False
    ).count()
    
    # 获取最近活动
    recent_activity = db.query(UsageStats).filter(
        UsageStats.user_id == current_user.id
    ).order_by(UsageStats.created_at.desc()).limit(10).all()
    
    return {
        "total_sessions": total_sessions,
        "favorite_sessions": favorite_sessions,
        "account_created": current_user.created_at,
        "last_login": current_user.last_login_at,
        "recent_activity": [
            {
                "action": a.action,
                "created_at": a.created_at
            }
            for a in recent_activity
        ]
    }
