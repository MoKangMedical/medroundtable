from fastapi import APIRouter, HTTPException
from typing import List, Dict

from backend.templates import templates

router = APIRouter(prefix="/templates", tags=["研究模板"])

@router.get("/list")
async def get_template_list():
    """获取所有可用模板列表"""
    return {
        "templates": templates.get_template_list()
    }

@router.get("/{template_id}")
async def get_template(template_id: str):
    """获取指定模板的详细内容"""
    template = templates.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.post("/generate/{template_id}")
async def generate_protocol(template_id: str, custom_data: dict = None):
    """
    根据模板生成研究方案
    
    custom_data: 自定义数据，用于填充模板中的占位符
    """
    try:
        if custom_data is None:
            custom_data = {}
        
        protocol = templates.generate_protocol(template_id, custom_data)
        return {
            "template_id": template_id,
            "protocol": protocol
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommend")
async def recommend_template(clinical_question: str):
    """
    根据临床问题推荐合适的研究模板
    
    clinical_question: 临床问题描述
    """
    recommendations = templates.recommend_template(clinical_question)
    return {
        "clinical_question": clinical_question,
        "recommendations": recommendations
    }
