from fastapi import APIRouter, HTTPException
from typing import Optional

from backend.literature import literature_search

router = APIRouter(prefix="/literature", tags=["文献检索"])

@router.get("/search")
async def search_literature(
    query: str,
    max_results: int = 10,
    sort: str = "relevance"
):
    """
    搜索PubMed文献
    
    参数:
    - query: 搜索关键词
    - max_results: 最大返回数量 (默认10)
    - sort: 排序方式 (relevance/date)
    """
    try:
        results = literature_search.search_pubmed(query, max_results, sort)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search-by-question")
async def search_by_question(question: str):
    """
    根据临床问题自动搜索相关文献
    
    参数:
    - question: 临床问题描述
    """
    try:
        results = literature_search.search_by_clinical_question(question)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/related/{pmid}")
async def get_related_articles(pmid: str, max_results: int = 5):
    """
    获取相关文献
    
    参数:
    - pmid: PubMed ID
    - max_results: 最大返回数量
    """
    try:
        articles = literature_search.get_related_articles(pmid, max_results)
        return {
            "pmid": pmid,
            "related_articles": articles
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
