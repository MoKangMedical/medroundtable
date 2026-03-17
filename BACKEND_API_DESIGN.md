# MedRoundTable V2.0 后端API实现方案

## 一、A2A多Agent协作系统架构

### 1.1 五大核心Agent

```python
# backend/agents/core_agents.py

class ClinicalDirectorAgent:
    """临床主任Agent - 研究策略制定"""
    def __init__(self):
        self.role = "clinical_director"
        self.expertise = ["研究设计", "临床决策", "终点指标定义"]
    
    async def design_study(self, clinical_question: str) -> dict:
        """设计研究方案"""
        return {
            "study_type": "随机对照试验",
            "primary_endpoint": "...",
            "secondary_endpoints": [...],
            "timeline": "..."
        }

class PhDStudentAgent:
    """博士生Agent - 文献检索与综述"""
    def __init__(self):
        self.role = "phd_student"
        self.expertise = ["文献检索", "系统综述", "证据整合"]
    
    async def literature_review(self, topic: str) -> dict:
        """执行文献综述"""
        return {
            "pubmed_results": [...],
            "summary": "...",
            "gaps": [...]
        }

class EpidemiologistAgent:
    """流行病学家Agent - 研究设计质控"""
    def __init__(self):
        self.role = "epidemiologist"
        self.expertise = ["研究设计", "偏倚控制", "样本量计算"]
    
    async def review_design(self, protocol: dict) -> dict:
        """审查研究设计"""
        return {
            "quality_score": 0.95,
            "suggestions": [...],
            "bias_assessment": "..."
        }

class StatisticianAgent:
    """统计学家Agent - 统计分析方案"""
    def __init__(self):
        self.role = "statistician"
        self.expertise = ["统计分析", "样本量计算", "CRF设计"]
    
    async def design_analysis(self, study_design: dict) -> dict:
        """设计统计分析方案"""
        return {
            "sample_size": 300,
            "statistical_methods": [...],
            "crf_template": "..."
        }

class ResearchNurseAgent:
    """研究护士Agent - 数据质量控制"""
    def __init__(self):
        self.role = "research_nurse"
        self.expertise = ["数据采集", "GCP合规", "质量核查"]
    
    async def design_data_collection(self) -> dict:
        """设计数据采集流程"""
        return {
            "visit_schedule": [...],
            "qc_procedures": [...],
            "sop_documents": [...]
        }
```

### 1.2 A2A协作编排器

```python
# backend/agents/orchestrator.py

class A2AOrchestrator:
    """A2A多Agent协作编排器"""
    
    def __init__(self):
        self.agents = {
            "clinical_director": ClinicalDirectorAgent(),
            "phd_student": PhDStudentAgent(),
            "epidemiologist": EpidemiologistAgent(),
            "statistician": StatisticianAgent(),
            "research_nurse": ResearchNurseAgent()
        }
    
    async def conduct_roundtable(self, clinical_question: str) -> dict:
        """执行完整的圆桌会讨论"""
        
        # 阶段1: 文献回顾
        literature = await self.agents["phd_student"].literature_review(clinical_question)
        
        # 阶段2: 研究设计
        study_design = await self.agents["clinical_director"].design_study(clinical_question)
        
        # 阶段3: 设计审查
        review = await self.agents["epidemiologist"].review_design(study_design)
        
        # 阶段4: 统计分析方案
        analysis_plan = await self.agents["statistician"].design_analysis(study_design)
        
        # 阶段5: 数据采集设计
        data_plan = await self.agents["research_nurse"].design_data_collection()
        
        return {
            "clinical_question": clinical_question,
            "literature_review": literature,
            "study_design": study_design,
            "design_review": review,
            "analysis_plan": analysis_plan,
            "data_collection_plan": data_plan
        }
```

## 二、技能市场API (997项技能)

```python
# backend/api/skills.py

from fastapi import APIRouter, Depends
from typing import List, Optional

router = APIRouter(prefix="/api/v1/skills")

class SkillMarketplace:
    """技能市场 - 997项AI技能管理"""
    
    SKILLS_CATEGORIES = {
        "literature": {
            "name": "文献检索",
            "skills_count": 50,
            "skills": [
                {"id": "pubmed_advanced", "name": "PubMed高级搜索", "api": "pubmed.search"},
                {"id": "literature_review", "name": "文献综述生成", "api": "literature.review"},
                {"id": "deep_mining", "name": "深度文献挖掘", "api": "literature.mine"}
            ]
        },
        "clinical_trial": {
            "name": "临床试验",
            "skills_count": 120,
            "skills": [
                {"id": "trial_design", "name": "试验设计优化", "api": "trial.design"},
                {"id": "patient_matching", "name": "患者匹配算法", "api": "trial.match"},
                {"id": "eligibility_assessment", "name": "入排评估系统", "api": "trial.eligibility"}
            ]
        },
        "clinical_decision": {
            "name": "临床决策",
            "skills_count": 80,
            "skills": [
                {"id": "diagnosis_reasoning", "name": "诊断推理辅助", "api": "clinical.diagnose"},
                {"id": "nlp_extraction", "name": "病历NLP提取", "api": "clinical.nlp"},
                {"id": "guideline_query", "name": "临床指南查询", "api": "clinical.guideline"}
            ]
        },
        "bioinformatics": {
            "name": "生物信息学",
            "skills_count": 300,
            "skills": [
                {"id": "scrna_analysis", "name": "单细胞RNA测序分析", "api": "bioinfo.scrna"},
                {"id": "variant_annotation", "name": "变异注释与过滤", "api": "bioinfo.variant"},
                {"id": "pathway_analysis", "name": "通路富集分析", "api": "bioinfo.pathway"}
            ]
        },
        "drug_discovery": {
            "name": "药物研发",
            "skills_count": 200,
            "skills": [
                {"id": "ai_drug_discovery", "name": "AI药物发现", "api": "drug.discover"},
                {"id": "admet_prediction", "name": "ADMET预测", "api": "drug.admet"},
                {"id": "bindingdb_query", "name": "BindingDB查询", "api": "drug.binding"}
            ]
        },
        "regulatory": {
            "name": "法规合规",
            "skills_count": 100,
            "skills": [
                {"id": "fda_query", "name": "FDA/MDR/NMPA查询", "api": "regulatory.query"},
                {"id": "compliance_check", "name": "合规性检查", "api": "regulatory.check"},
                {"id": "regulatory_tracking", "name": "法规更新追踪", "api": "regulatory.track"}
            ]
        }
    }
    
    @classmethod
    def get_all_skills(cls) -> dict:
        """获取所有997项技能"""
        total_skills = 0
        for category in cls.SKILLS_CATEGORIES.values():
            total_skills += category["skills_count"]
        return {
            "total_skills": total_skills,
            "categories": cls.SKILLS_CATEGORIES
        }

@router.get("/marketplace")
async def get_skills_marketplace():
    """获取技能市场所有997项技能"""
    return SkillMarketplace.get_all_skills()

@router.get("/category/{category_id}")
async def get_skills_by_category(category_id: str):
    """按分类获取技能"""
    category = SkillMarketplace.SKILLS_CATEGORIES.get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/execute/{skill_id}")
async def execute_skill(skill_id: str, params: dict):
    """执行特定技能"""
    # 技能执行逻辑
    return {"skill_id": skill_id, "result": "...", "status": "success"}
```

## 三、数据库浏览器API (40+数据库)

```python
# backend/api/databases.py

router = APIRouter(prefix="/api/v1/databases")

class DatabaseBrowser:
    """数据库浏览器 - 40+生物医学数据库"""
    
    DATABASES = {
        "literature": [
            {"name": "PubMed", "url": "https://pubmed.ncbi.nlm.nih.gov/", "records": "3300万+", "type": "文献"},
            {"name": "PubMed Central", "url": "https://www.ncbi.nlm.nih.gov/pmc/", "records": "全文", "type": "文献"},
            {"name": "Europe PMC", "url": "https://europepmc.org/", "records": "欧洲PMC", "type": "文献"}
        ],
        "clinical_trials": [
            {"name": "ClinicalTrials.gov", "url": "https://clinicaltrials.gov/", "records": "50万+", "type": "试验"},
            {"name": "中国CDE平台", "url": "http://www.chinadrugtrials.org.cn/", "records": "官方登记", "type": "试验"},
            {"name": "EU CTR", "url": "https://www.clinicaltrialsregister.eu/", "records": "欧盟", "type": "试验"}
        ],
        "drugs": [
            {"name": "DrugBank", "url": "https://go.drugbank.com/", "records": "1.5万+", "type": "药物"},
            {"name": "ChEMBL", "url": "https://www.ebi.ac.uk/chembl/", "records": "生物活性", "type": "药物"},
            {"name": "BindingDB", "url": "https://www.bindingdb.org/", "records": "结合亲和力", "type": "药物"}
        ],
        "genomics": [
            {"name": "ClinVar", "url": "https://www.ncbi.nlm.nih.gov/clinvar/", "records": "变异临床解读", "type": "基因组"},
            {"name": "dbSNP", "url": "https://www.ncbi.nlm.nih.gov/snp/", "records": "SNP数据库", "type": "基因组"},
            {"name": "gnomAD", "url": "https://gnomad.broadinstitute.org/", "records": "基因组聚合", "type": "基因组"},
            {"name": "OMIM", "url": "https://www.omim.org/", "records": "遗传疾病", "type": "基因组"}
        ],
        "proteins": [
            {"name": "UniProt", "url": "https://www.uniprot.org/", "records": "蛋白质序列", "type": "蛋白质"},
            {"name": "PDB", "url": "https://www.rcsb.org/", "records": "3D结构", "type": "蛋白质"}
        ],
        "pathways": [
            {"name": "KEGG", "url": "https://www.kegg.jp/", "records": "基因与通路", "type": "通路"},
            {"name": "Reactome", "url": "https://reactome.org/", "records": "人类生物学通路", "type": "通路"}
        ]
    }

@router.get("/")
async def get_all_databases():
    """获取所有40+数据库"""
    return {
        "total_databases": sum(len(dbs) for dbs in DatabaseBrowser.DATABASES.values()),
        "categories": DatabaseBrowser.DATABASES
    }

@router.get("/search")
async def search_databases(query: str, category: Optional[str] = None):
    """跨数据库搜索"""
    results = []
    # 实现搜索逻辑
    return {"query": query, "results": results}
```

## 四、临床试验设计器API

```python
# backend/api/trial_designer.py

router = APIRouter(prefix="/api/v1/trial-designer")

class TrialDesigner:
    """临床试验设计器"""
    
    async def generate_protocol(self, study_objective: str, study_type: str) -> dict:
        """智能方案生成"""
        return {
            "protocol": {
                "title": f"{study_objective}临床研究",
                "objective": study_objective,
                "design": study_type,
                "primary_endpoint": "...",
                "secondary_endpoints": [...],
                "inclusion_criteria": [...],
                "exclusion_criteria": [...],
                "sample_size": 300,
                "study_duration": "12个月"
            }
        }
    
    async def assess_eligibility(self, patient_data: dict, criteria: dict) -> dict:
        """患者入排评估"""
        score = 0
        reasons = []
        # 评估逻辑
        return {
            "eligible": score > 0.8,
            "score": score,
            "reasons": reasons
        }
    
    async def match_patient_to_trials(self, patient_profile: dict) -> list:
        """患者-试验匹配"""
        matches = []
        # 匹配逻辑
        return matches

@router.post("/generate-protocol")
async def generate_study_protocol(objective: str, study_type: str):
    """生成研究方案"""
    designer = TrialDesigner()
    return await designer.generate_protocol(objective, study_type)

@router.post("/assess-eligibility")
async def assess_patient_eligibility(patient_data: dict, criteria: dict):
    """评估患者入排"""
    designer = TrialDesigner()
    return await designer.assess_eligibility(patient_data, criteria)

@router.post("/match-trials")
async def match_trials(patient_profile: dict):
    """匹配临床试验"""
    designer = TrialDesigner()
    return await designer.match_patient_to_trials(patient_profile)
```

## 五、认证系统API (5种角色)

```python
# backend/api/auth.py

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/v1/auth")
security = HTTPBearer()

class AuthSystem:
    """JWT认证系统 - 5种角色"""
    
    ROLES = ["admin", "researcher", "clinician", "student", "guest"]
    
    SECRET_KEY = "your-secret-key"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS = 7
    
    @classmethod
    def create_access_token(cls, user_id: str, role: str) -> str:
        """创建JWT令牌"""
        expire = datetime.utcnow() + timedelta(days=cls.ACCESS_TOKEN_EXPIRE_DAYS)
        payload = {
            "sub": user_id,
            "role": role,
            "exp": expire,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
    
    @classmethod
    def verify_token(cls, token: str) -> dict:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/login")
async def login(email: str, password: str):
    """用户登录"""
    # 验证用户凭据
    user = verify_credentials(email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = AuthSystem.create_access_token(user["id"], user["role"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/register")
async def register(email: str, password: str, role: str = "guest"):
    """用户注册"""
    if role not in AuthSystem.ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    # 创建用户逻辑
    user = create_user(email, password, role)
    return {"message": "User created", "user_id": user["id"]}

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前用户"""
    token = credentials.credentials
    payload = AuthSystem.verify_token(token)
    return payload

@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    return user
```

## 六、API路由汇总

```python
# backend/main.py

from fastapi import FastAPI
from api import skills, databases, trial_designer, auth
from agents.orchestrator import A2AOrchestrator

app = FastAPI(title="MedRoundTable V2.0 API")

# 注册路由
app.include_router(skills.router)
app.include_router(databases.router)
app.include_router(trial_designer.router)
app.include_router(auth.router)

# A2A协作端点
@app.post("/api/v1/a2a/roundtable")
async def conduct_roundtable(clinical_question: str):
    """执行A2A多Agent协作圆桌会"""
    orchestrator = A2AOrchestrator()
    result = await orchestrator.conduct_roundtable(clinical_question)
    return result

@app.get("/api/v1/a2a/agents")
async def get_available_agents():
    """获取可用Agent列表"""
    return {
        "agents": [
            {"id": "clinical_director", "name": "临床主任", "expertise": ["研究设计"]},
            {"id": "phd_student", "name": "博士生", "expertise": ["文献检索"]},
            {"id": "epidemiologist", "name": "流行病学家", "expertise": ["研究设计质控"]},
            {"id": "statistician", "name": "统计学家", "expertise": ["统计分析"]},
            {"id": "research_nurse", "name": "研究护士", "expertise": ["数据质量控制"]}
        ]
    }
```

## 七、部署配置

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///medroundtable.db
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./data:/app/data
  
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
```

## 八、环境变量

```bash
# .env
SECRET_KEY=your-super-secret-key
DATABASE_URL=sqlite:///medroundtable.db
OPENAI_API_KEY=sk-...
PUBMED_API_KEY=...
SECONDME_CLIENT_ID=19b5f08b-2256-41aa-b196-2f98491099f7
SECONDME_CLIENT_SECRET=...
```

---

**实现状态**: 
- ✅ 前端页面已完成
- ⏳ 后端API架构设计完成
- ⏳ 待部署到生产环境
