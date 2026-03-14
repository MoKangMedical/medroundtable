"""
MedRoundTable 自研认证系统
替代 Second Me OAuth，实现完全自主的用户管理
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
import bcrypt
from enum import Enum

# 配置
SECRET_KEY = "your-secret-key-change-this-in-production"  # 生产环境请更换
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

router = APIRouter(prefix="/api/v2/auth", tags=["认证"])
security = HTTPBearer()

# ============ 数据模型 ============

class UserRole(str, Enum):
    ADMIN = "admin"
    RESEARCHER = "researcher"
    CLINICIAN = "clinician"
    STUDENT = "student"
    GUEST = "guest"

class User(BaseModel):
    id: str
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.RESEARCHER
    institution: Optional[str] = None
    department: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None
    avatar_url: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.RESEARCHER
    institution: Optional[str] = None
    department: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User

class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

# ============ 模拟数据库 ============
# 实际项目中使用真实数据库
_users_db = {}
_tokens_db = {}

# ============ 工具函数 ============

def hash_password(password: str) -> str:
    """密码哈希"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建JWT令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, expire

def decode_token(token: str) -> Optional[Dict]:
    """解码JWT令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """获取当前用户"""
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None or user_id not in _users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_data = _users_db[user_id]
    return User(**{k: v for k, v in user_data.items() if k != "password_hash"})

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return current_user

# ============ API端点 ============

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_create: UserCreate):
    """
    用户注册
    
    - **email**: 邮箱地址（唯一）
    - **username**: 用户名（唯一）
    - **password**: 密码（至少8位）
    - **full_name**: 真实姓名（可选）
    - **role**: 角色（默认为researcher）
    - **institution**: 机构（可选）
    - **department**: 科室（可选）
    """
    # 检查邮箱是否已存在
    for user in _users_db.values():
        if user["email"] == user_create.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被注册"
            )
        if user["username"] == user_create.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该用户名已被使用"
            )
    
    # 创建用户
    user_id = f"user_{len(_users_db) + 1:06d}"
    hashed_password = hash_password(user_create.password)
    
    user_data = {
        "id": user_id,
        "email": user_create.email,
        "username": user_create.username,
        "password_hash": hashed_password,
        "full_name": user_create.full_name,
        "role": user_create.role,
        "institution": user_create.institution,
        "department": user_create.department,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "last_login": None,
        "avatar_url": None
    }
    
    _users_db[user_id] = user_data
    
    # 创建访问令牌
    access_token, expire = create_access_token(data={"sub": user_id, "email": user_create.email})
    
    # 返回用户信息（不包含密码）
    user_response = User(**{k: v for k, v in user_data.items() if k != "password_hash"})
    
    return Token(
        access_token=access_token,
        expires_in=int((expire - datetime.utcnow()).total_seconds()),
        user=user_response
    )

@router.post("/login", response_model=Token)
async def login(user_login: UserLogin):
    """
    用户登录
    
    - **email**: 邮箱地址
    - **password**: 密码
    """
    # 查找用户
    user = None
    for u in _users_db.values():
        if u["email"] == user_login.email:
            user = u
            break
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 验证密码
    if not verify_password(user_login.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户是否激活
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用，请联系管理员"
        )
    
    # 更新最后登录时间
    user["last_login"] = datetime.utcnow()
    
    # 创建访问令牌
    access_token, expire = create_access_token(data={"sub": user["id"], "email": user["email"]})
    
    # 返回用户信息
    user_response = User(**{k: v for k, v in user.items() if k != "password_hash"})
    
    return Token(
        access_token=access_token,
        expires_in=int((expire - datetime.utcnow()).total_seconds()),
        user=user_response
    )

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    用户登出
    
    使当前令牌失效（可选实现令牌黑名单）
    """
    # 可选：将令牌加入黑名单
    return {"message": "登出成功"}

@router.get("/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """
    获取当前用户信息
    
    需要认证令牌
    """
    return current_user

@router.put("/me", response_model=User)
async def update_me(
    full_name: Optional[str] = None,
    institution: Optional[str] = None,
    department: Optional[str] = None,
    avatar_url: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    更新当前用户信息
    """
    user_data = _users_db[current_user.id]
    
    if full_name:
        user_data["full_name"] = full_name
    if institution:
        user_data["institution"] = institution
    if department:
        user_data["department"] = department
    if avatar_url:
        user_data["avatar_url"] = avatar_url
    
    return User(**{k: v for k, v in user_data.items() if k != "password_hash"})

@router.post("/password/change")
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_active_user)
):
    """
    修改密码
    
    - **old_password**: 旧密码
    - **new_password**: 新密码（至少8位）
    """
    user_data = _users_db[current_user.id]
    
    # 验证旧密码
    if not verify_password(password_change.old_password, user_data["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )
    
    # 更新密码
    user_data["password_hash"] = hash_password(password_change.new_password)
    
    return {"message": "密码修改成功"}

@router.post("/password/reset")
async def reset_password(reset_request: PasswordReset):
    """
    请求密码重置
    
    发送重置链接到用户邮箱（需要集成邮件服务）
    """
    # 查找用户
    user = None
    for u in _users_db.values():
        if u["email"] == reset_request.email:
            user = u
            break
    
    # 无论用户是否存在，都返回相同消息（安全考虑）
    if user:
        # 生成重置令牌
        reset_token = create_access_token(
            data={"sub": user["id"], "type": "password_reset"},
            expires_delta=timedelta(hours=1)
        )[0]
        
        # TODO: 发送邮件
        # 实际项目中这里应该发送包含reset_token的邮件
        print(f"密码重置令牌（应通过邮件发送）: {reset_token}")
    
    return {"message": "如果该邮箱存在，我们将发送密码重置链接"}

@router.get("/users", response_model=list[User])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
):
    """
    获取用户列表（仅管理员）
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以查看用户列表"
        )
    
    users = []
    for user_data in list(_users_db.values())[skip:skip+limit]:
        users.append(User(**{k: v for k, v in user_data.items() if k != "password_hash"}))
    
    return users

# ============ 初始化测试用户 ============

def init_test_users():
    """初始化测试用户"""
    if not _users_db:
        # 创建管理员用户
        admin_data = {
            "id": "user_000001",
            "email": "admin@medroundtable.com",
            "username": "admin",
            "password_hash": hash_password("admin123"),
            "full_name": "系统管理员",
            "role": UserRole.ADMIN,
            "institution": "MedRoundTable",
            "department": "技术部",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "last_login": None,
            "avatar_url": None
        }
        _users_db["user_000001"] = admin_data
        
        # 创建测试研究员
        researcher_data = {
            "id": "user_000002",
            "email": "researcher@medroundtable.com",
            "username": "researcher",
            "password_hash": hash_password("research123"),
            "full_name": "测试研究员",
            "role": UserRole.RESEARCHER,
            "institution": "北京协和医院",
            "department": "心内科",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "last_login": None,
            "avatar_url": None
        }
        _users_db["user_000002"] = researcher_data
        
        print("✅ 初始化测试用户完成")
        print("   - 管理员: admin@medroundtable.com / admin123")
        print("   - 研究员: researcher@medroundtable.com / research123")

# 启动时初始化
init_test_users()

if __name__ == "__main__":
    # 测试
    import asyncio
    
    async def test():
        # 测试登录
        token = await login(UserLogin(email="admin@medroundtable.com", password="admin123"))
        print(f"登录成功: {token.user.username}")
    
    asyncio.run(test())
