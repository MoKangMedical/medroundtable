"""
数据库查询 API

统一访问平台已编目的生物医学数据库目录。
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.services.platform_catalog import get_platform_databases
from backend.services.database_service import DatabaseService
from backend.upload_models import DatabaseResponse, PublicDatasetSnapshotCreate

router = APIRouter(prefix="/api/v2/databases", tags=["数据库查询"])

# ============ 数据模型 ============

class DatabaseInfo(BaseModel):
    id: str
    name: str
    description: str
    category: str
    url: str
    enabled: bool

class QueryRequest(BaseModel):
    database: str
    query: str
    filters: Optional[Dict[str, Any]] = {}
    limit: int = 20

class QueryResponse(BaseModel):
    database: str
    query: str
    total_results: int
    results: List[Dict[str, Any]]
    execution_time: float

# ============ 数据库注册表 ============

DATABASES = {
    database["id"]: {
        "id": database["id"],
        "name": database["name"],
        "description": database["description"],
        "category": database["category"],
        "url": database["url"],
        "enabled": True,
        "access_mode": database.get("access_mode"),
        "integration": database.get("integration"),
        "recommended_agent": database.get("recommended_agent"),
        "tags": database.get("tags", []),
    }
    for database in get_platform_databases()
}

# ============ API端点 ============

@router.get("/", response_model=List[DatabaseInfo])
async def list_databases(
    category: Optional[str] = Query(None, description="按分类筛选"),
    enabled_only: bool = Query(True, description="仅显示启用的数据库")
):
    """
    获取所有数据库列表
    
    分类: 文献/临床试验/药物/基因组/蛋白质/通路/疾病/法规
    """
    databases = []
    for db_id, db_info in DATABASES.items():
        if category and db_info["category"] != category:
            continue
        if enabled_only and not db_info["enabled"]:
            continue
        databases.append(DatabaseInfo(**db_info))
    
    return databases

@router.get("/categories")
async def get_categories():
    """获取数据库分类列表"""
    categories = {}
    for db_info in DATABASES.values():
        cat = db_info["category"]
        if cat not in categories:
            categories[cat] = {"name": cat, "count": 0, "databases": []}
        categories[cat]["count"] += 1
        categories[cat]["databases"].append(db_info["id"])
    
    return list(categories.values())

@router.get("/{db_id}")
async def get_database(db_id: str):
    """获取数据库详情"""
    if db_id not in DATABASES:
        raise HTTPException(status_code=404, detail=f"数据库 {db_id} 不存在")
    
    return DatabaseInfo(**DATABASES[db_id])

@router.post("/query", response_model=QueryResponse)
async def query_database(request: QueryRequest):
    """
    统一查询接口
    
    参数:
    - database: 数据库ID
    - query: 查询内容
    - filters: 筛选条件
    - limit: 返回数量限制
    """
    if request.database not in DATABASES:
        raise HTTPException(status_code=404, detail=f"数据库 {request.database} 不存在")
    
    if not DATABASES[request.database]["enabled"]:
        raise HTTPException(status_code=400, detail=f"数据库 {request.database} 未启用")
    
    # 根据数据库类型执行查询
    try:
        results = await _execute_query(request)
        return QueryResponse(
            database=request.database,
            query=request.query,
            total_results=len(results),
            results=results,
            execution_time=0.5  # 模拟执行时间
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.post("/snapshots", response_model=DatabaseResponse)
async def save_query_snapshot(request: PublicDatasetSnapshotCreate):
    """将公开数据库查询结果保存到服务器，作为后续分析可复用数据集。"""
    if request.database not in DATABASES:
        raise HTTPException(status_code=404, detail=f"数据库 {request.database} 不存在")

    query_request = QueryRequest(
        database=request.database,
        query=request.query,
        filters=request.filters or {},
        limit=request.limit,
    )
    results = await _execute_query(query_request)
    saved = await DatabaseService.save_public_dataset_snapshot(
        source_database_id=request.database,
        source_database_name=DATABASES[request.database]["name"],
        source_url=DATABASES[request.database]["url"],
        query=request.query,
        results=results,
        filters=request.filters or {},
        name=request.name,
        description=request.description,
        uploaded_by=request.uploaded_by,
        roundtable_id=request.roundtable_id,
        protocol_id=request.protocol_id,
    )
    return saved

async def _execute_query(request: QueryRequest) -> List[Dict]:
    """执行数据库查询"""
    db_id = request.database
    query = request.query
    
    # 模拟查询结果
    # 实际实现需要集成各个数据库的API
    
    if db_id == "pubmed":
        return _mock_pubmed_results(query, request.limit)
    elif db_id == "clinicaltrials":
        return _mock_clinicaltrials_results(query, request.limit)
    elif db_id == "drugbank":
        return _mock_drugbank_results(query, request.limit)
    elif db_id == "clinvar":
        return _mock_clinvar_results(query, request.limit)
    else:
        return _mock_generic_results(db_id, query, request.limit)

def _mock_pubmed_results(query: str, limit: int) -> List[Dict]:
    """模拟PubMed查询结果"""
    return [
        {
            "pmid": f"3800000{i}",
            "title": f"关于{query}的最新研究进展",
            "authors": ["Zhang S", "Li W", "Wang H"],
            "journal": "Nature Medicine",
            "year": 2024,
            "doi": f"10.1000/{i}"
        }
        for i in range(1, min(limit + 1, 6))
    ]

def _mock_clinicaltrials_results(query: str, limit: int) -> List[Dict]:
    """模拟ClinicalTrials查询结果"""
    return [
        {
            "nct_id": f"NCT0560000{i}",
            "title": f"{query}治疗的随机对照试验",
            "phase": "Phase III",
            "status": "Recruiting",
            "sponsor": "National Cancer Institute",
            "locations": ["USA", "China", "EU"]
        }
        for i in range(1, min(limit + 1, 6))
    ]

def _mock_drugbank_results(query: str, limit: int) -> List[Dict]:
    """模拟DrugBank查询结果"""
    return [
        {
            "drugbank_id": f"DB0000{i}",
            "name": f"{query}抑制剂",
            "type": "Small molecule",
            "groups": ["approved", " investigational"],
            "mechanism": f"抑制{query}信号通路"
        }
        for i in range(1, min(limit + 1, 6))
    ]

def _mock_clinvar_results(query: str, limit: int) -> List[Dict]:
    """模拟ClinVar查询结果"""
    return [
        {
            "variant_id": f"VCV0000000{i}",
            "gene": query.upper(),
            "chromosome": "chr1",
            "position": 1000000 + i * 100,
            "significance": "Pathogenic" if i % 2 == 0 else "Benign",
            "condition": f"{query}相关疾病"
        }
        for i in range(1, min(limit + 1, 6))
    ]

def _mock_generic_results(db_id: str, query: str, limit: int) -> List[Dict]:
    """通用模拟结果"""
    return [
        {
            "id": f"{db_id}_{i}",
            "name": f"{query} - 结果{i}",
            "description": f"来自{DATABASES.get(db_id, {}).get('name', db_id)}的查询结果"
        }
        for i in range(1, min(limit + 1, 6))
    ]

# ============ 特色查询接口 ============

@router.get("/pubmed/advanced")
async def advanced_pubmed_search(
    query: str = Query(..., description="搜索关键词"),
    author: Optional[str] = Query(None, description="作者"),
    journal: Optional[str] = Query(None, description="期刊"),
    year_from: Optional[int] = Query(None, description="起始年份"),
    year_to: Optional[int] = Query(None, description="结束年份"),
    article_type: Optional[str] = Query(None, description="文章类型"),
    max_results: int = Query(20, description="最大结果数")
):
    """
    高级PubMed搜索
    
    支持多条件组合搜索
    """
    filters = {
        "author": author,
        "journal": journal,
        "year_from": year_from,
        "year_to": year_to,
        "article_type": article_type
    }
    
    results = _mock_pubmed_results(query, max_results)
    return {
        "query": query,
        "filters": {k: v for k, v in filters.items() if v},
        "total_results": len(results),
        "results": results
    }

@router.get("/clinicaltrials/search")
async def search_clinical_trials(
    condition: str = Query(..., description="疾病/适应证"),
    intervention: Optional[str] = Query(None, description="干预措施"),
    phase: Optional[str] = Query(None, description="试验阶段"),
    status: Optional[str] = Query(None, description="试验状态"),
    location: Optional[str] = Query(None, description="地点"),
    max_results: int = Query(20, description="最大结果数")
):
    """
    临床试验高级搜索
    """
    results = _mock_clinicaltrials_results(condition, max_results)
    return {
        "condition": condition,
        "intervention": intervention,
        "phase": phase,
        "status": status,
        "total_results": len(results),
        "results": results
    }

@router.get("/drugbank/search")
async def search_drugs(
    name: str = Query(..., description="药物名称"),
    mechanism: Optional[str] = Query(None, description="作用机制"),
    target: Optional[str] = Query(None, description="靶点"),
    max_results: int = Query(20, description="最大结果数")
):
    """
    药物数据库搜索
    """
    results = _mock_drugbank_results(name, max_results)
    return {
        "query": name,
        "mechanism": mechanism,
        "target": target,
        "total_results": len(results),
        "results": results
    }
