"""
MedRoundTable 自研认证系统集成指南

从 Second Me OAuth 迁移到自研认证系统
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v2/auth", tags=["认证"])

# 导入自研认证模块
from backend.routes.auth.custom_auth import router as custom_auth_router

# 包含自研认证路由
# 这将覆盖或补充原有的Second Me路由
