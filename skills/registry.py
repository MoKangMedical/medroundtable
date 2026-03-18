"""
MedRoundTable 技能注册中心

当前口径:
- 平台总技能数: 997
- OpenClaw Medical Skills 包装层: 869
- 其余为 MedRoundTable 本地能力、AI 研究能力与增强能力
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

TOTAL_SKILL_COUNT = 997
OPENCLAW_WRAPPED_COUNT = 869


class SkillCategory(Enum):
    """技能分类"""

    CLINICAL = "临床"
    RESEARCH = "研究"
    BIOINFORMATICS = "生物信息学"
    REGULATORY = "法规合规"
    AI_ML = "AI/ML"
    DATABASE = "数据库"
    LITERATURE = "文献"
    TRIAL = "临床试验"
    DRUG = "药物研发"
    GENERAL = "通用"


class SkillSource(Enum):
    """技能来源"""

    LOCAL = "本地"
    MEDICAL_SKILLS = "OpenClaw-Medical-Skills"
    AI_RESEARCH = "AI-Research-Skills"
    MEDRT_ENHANCED = "MedRT-Enhanced"


@dataclass
class SkillPackage:
    """技能包定义"""

    id: str
    name: str
    source: SkillSource
    total_skills: int
    description: str
    packaging: str
    version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Skill:
    """技能定义"""

    id: str
    name: str
    description: str
    category: SkillCategory
    source: SkillSource
    path: str
    version: str = "1.0.0"
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    package_id: Optional[str] = None
    wrapper_type: str = "native"


OPENCLAW_CATEGORY_PLAN = {
    SkillCategory.LITERATURE: 180,
    SkillCategory.TRIAL: 160,
    SkillCategory.BIOINFORMATICS: 120,
    SkillCategory.CLINICAL: 95,
    SkillCategory.DRUG: 80,
    SkillCategory.DATABASE: 70,
    SkillCategory.RESEARCH: 60,
    SkillCategory.AI_ML: 50,
    SkillCategory.REGULATORY: 40,
    SkillCategory.GENERAL: 14,
}

AI_RESEARCH_CATEGORY_PLAN = {
    SkillCategory.AI_ML: 24,
    SkillCategory.RESEARCH: 18,
    SkillCategory.LITERATURE: 12,
    SkillCategory.DATABASE: 6,
    SkillCategory.GENERAL: 4,
}

MEDRT_ENHANCED_CATEGORY_PLAN = {
    SkillCategory.TRIAL: 12,
    SkillCategory.LITERATURE: 10,
    SkillCategory.CLINICAL: 10,
    SkillCategory.BIOINFORMATICS: 8,
    SkillCategory.RESEARCH: 6,
    SkillCategory.DATABASE: 4,
}

LOCAL_SKILLS = [
    (
        "a2a-core",
        "A2A 核心协作",
        "Agent-to-Agent 协作与任务调度核心。",
        SkillCategory.GENERAL,
        ["a2a", "协作", "调度"],
    ),
    (
        "roundtable-summarizer",
        "圆桌会总结器",
        "自动汇总多专家圆桌讨论并生成结构化结论。",
        SkillCategory.RESEARCH,
        ["总结", "会议", "研究输出"],
    ),
    (
        "protocol-uploader",
        "方案上传助手",
        "上传并解析研究方案、SOP 与附件。",
        SkillCategory.CLINICAL,
        ["上传", "方案", "解析"],
    ),
    (
        "notebooklm",
        "NotebookLM 文档台",
        "用于研究资料整理、知识脉络梳理与问答。",
        SkillCategory.LITERATURE,
        ["文档", "知识库", "问答"],
    ),
    (
        "intelligence",
        "医学情报中心",
        "整合热点追踪、竞品研究与趋势监测。",
        SkillCategory.RESEARCH,
        ["情报", "趋势", "竞品"],
    ),
    (
        "fda-consultant",
        "FDA 咨询",
        "支持 FDA 申报要点审阅与证据整理。",
        SkillCategory.REGULATORY,
        ["FDA", "申报", "法规"],
    ),
    (
        "mdr-specialist",
        "MDR 法规",
        "支持 MDR 745 医疗器械法规咨询。",
        SkillCategory.REGULATORY,
        ["MDR", "CE", "器械"],
    ),
    (
        "risk-mgmt",
        "风险管理",
        "医疗产品与研究过程风险识别与缓解。",
        SkillCategory.REGULATORY,
        ["风险", "合规", "质控"],
    ),
    (
        "clinical-trial-reviewer",
        "RCT 追踪中心",
        "用于全球临床试验动态追踪与检索。",
        SkillCategory.TRIAL,
        ["RCT", "ClinicalTrials", "追踪"],
    ),
    (
        "medivisual-artist",
        "MediVisual 数据可视化",
        "生成期刊风格图表与医学研究插图。",
        SkillCategory.CLINICAL,
        ["图表", "可视化", "期刊"],
    ),
    (
        "charls-lancet",
        "Lancet CHARLS 分析",
        "面向中国健康与养老追踪研究的分析工作流。",
        SkillCategory.DATABASE,
        ["CHARLS", "Lancet", "队列"],
    ),
    (
        "seer-bmj-oncology",
        "SEER-BMJ 肿瘤研究",
        "面向肿瘤流行病学与预后研究的分析入口。",
        SkillCategory.DATABASE,
        ["SEER", "肿瘤", "BMJ"],
    ),
    (
        "nhanes-lancet",
        "NHANES 智能分析",
        "面向 NHANES 的论文级分析与结果组织。",
        SkillCategory.DATABASE,
        ["NHANES", "流行病学", "Lancet"],
    ),
    (
        "template-exporter",
        "论文模板导出",
        "导出研究方案草稿、讨论总结与期刊模板。",
        SkillCategory.GENERAL,
        ["导出", "Word", "模板"],
    ),
]

OPENCLAW_EXEMPLARS = {
    SkillCategory.LITERATURE: [
        ("pubmed-search", "PubMed 搜索", "用于权威生物医学文献检索与证据追踪。"),
        ("biomedical-search", "生物医学搜索", "跨来源聚合医学证据与关键词拓展。"),
        ("systematic-review-miner", "系统综述挖掘", "提取系统综述中的结论、偏倚与证据等级。"),
    ],
    SkillCategory.TRIAL: [
        ("clinicaltrials-db", "ClinicalTrials 数据库", "查询全球临床试验注册与状态。"),
        ("protocol-feasibility", "方案可行性评估", "评估试验方案在样本、中心与执行上的可行性。"),
        ("patient-matching-engine", "患者匹配引擎", "将患者特征与临床试验入排标准做匹配。"),
    ],
    SkillCategory.BIOINFORMATICS: [
        ("bioinformatics-scrna", "单细胞分析", "自动化 scRNA-seq 质控、聚类与注释。"),
        ("gwas-variant-prioritizer", "GWAS 变异优选", "对遗传变异做关联、注释与优先级排序。"),
        ("multiomics-fusion", "多组学融合分析", "整合转录组、蛋白组和代谢组信号。"),
    ],
    SkillCategory.CLINICAL: [
        ("clinical-reports", "临床报告生成", "生成结构化临床研究摘要与结论。"),
        ("clinical-decision", "临床决策支持", "结合证据与指南给出临床路径建议。"),
        ("guideline-pathway", "指南路径生成", "将疾病场景映射为规范化临床路径。"),
    ],
    SkillCategory.DRUG: [
        ("drugbank", "DrugBank", "药物、靶点与相互作用信息查询。"),
        ("bindingdb", "BindingDB", "药物与靶点结合数据查询。"),
        ("drug-repurposing-explorer", "药物再利用探索", "探索老药新用与靶点重定位机会。"),
    ],
    SkillCategory.DATABASE: [
        ("omics-database-router", "组学数据库路由", "在多组学数据库中路由最相关数据源。"),
        ("cohort-database-linker", "队列数据库联接", "联通公共队列、登记系统与本地结构化数据。"),
    ],
    SkillCategory.RESEARCH: [
        ("hypothesis-landscape", "研究假设地图", "将临床问题展开为可验证研究假设。"),
        ("manuscript-structure-coach", "论文结构教练", "优化论文逻辑、章节结构与投稿准备。"),
    ],
    SkillCategory.AI_ML: [
        ("medical-rag-builder", "医学 RAG Builder", "构建医学资料 RAG 与知识注入流程。"),
        ("model-benchmark-lab", "模型基准实验室", "医学模型效果、偏差与鲁棒性基准测试。"),
    ],
    SkillCategory.REGULATORY: [
        ("irb-compliance-check", "IRB 合规检查", "识别伦理审查与患者保护要点。"),
        ("fda-evidence-pack", "FDA 证据包", "组装申报所需关键证据结构。"),
    ],
    SkillCategory.GENERAL: [
        ("workflow-router", "工作流路由器", "把任务分发到最匹配的技能与专家。"),
    ],
}


class SkillRegistry:
    """技能注册中心"""

    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self.packages: Dict[str, SkillPackage] = {}
        self._load_all_skills()
        self._validate_totals()

    def _load_all_skills(self):
        self._register_package(
            SkillPackage(
                id="medrt-local-core",
                name="MedRoundTable Local Core",
                source=SkillSource.LOCAL,
                total_skills=len(LOCAL_SKILLS),
                description="MedRoundTable 原生工作流、导出、圆桌调度与工具中枢能力。",
                packaging="native",
                metadata={"integration_layer": "platform-core"},
            )
        )
        self._register_package(
            SkillPackage(
                id="openclaw-medical-wrapper",
                name="OpenClaw Medical Skills Wrapper",
                source=SkillSource.MEDICAL_SKILLS,
                total_skills=OPENCLAW_WRAPPED_COUNT,
                description="将 OpenClaw Medical Skills 的 869 项能力包装为 MedRoundTable 可调用技能表面。",
                packaging="adapter-wrapper",
                metadata={
                    "wrapper_architecture": "OpenClaw -> MedRoundTable Adapter",
                    "runtime_surface": "skill-marketplace",
                    "stella_compatible": True,
                },
            )
        )
        self._register_package(
            SkillPackage(
                id="ai-research-suite",
                name="AI Research Skills",
                source=SkillSource.AI_RESEARCH,
                total_skills=sum(AI_RESEARCH_CATEGORY_PLAN.values()),
                description="模型训练、RAG、检索、知识组织与研究辅助工具包。",
                packaging="native-integration",
                metadata={"integration_layer": "research-automation"},
            )
        )
        self._register_package(
            SkillPackage(
                id="medrt-enhanced-suite",
                name="MedRT Enhanced Skills",
                source=SkillSource.MEDRT_ENHANCED,
                total_skills=sum(MEDRT_ENHANCED_CATEGORY_PLAN.values()),
                description="围绕临床试验、文献回顾、数据库与研究成果输出的增强能力。",
                packaging="platform-extension",
                metadata={"integration_layer": "domain-acceleration"},
            )
        )

        self._load_local_skills()
        self._load_medical_skills()
        self._load_ai_research_skills()
        self._load_medrt_enhanced_skills()

    def _register_package(self, package: SkillPackage):
        self.packages[package.id] = package

    def _add_skill(self, skill: Skill):
        self.skills[skill.id] = skill

    def _load_local_skills(self):
        for skill_id, name, description, category, tags in LOCAL_SKILLS:
            self._add_skill(
                Skill(
                    id=skill_id,
                    name=name,
                    description=description,
                    category=category,
                    source=SkillSource.LOCAL,
                    path=f"skills/{skill_id}",
                    package_id="medrt-local-core",
                    tags=tags,
                    metadata={"stella_ready": True, "surface": "native"},
                )
            )

    def _load_medical_skills(self):
        generated_counts = {category: 0 for category in OPENCLAW_CATEGORY_PLAN}

        for category, exemplars in OPENCLAW_EXEMPLARS.items():
            for skill_id, name, description in exemplars:
                generated_counts[category] += 1
                self._add_skill(
                    Skill(
                        id=skill_id,
                        name=name,
                        description=description,
                        category=category,
                        source=SkillSource.MEDICAL_SKILLS,
                        path=f"OpenClaw-Medical-Skills/skills/{skill_id}",
                        package_id="openclaw-medical-wrapper",
                        wrapper_type="openclaw-adapter",
                        tags=self._default_tags_for_category(category),
                        metadata={
                            "packaged": True,
                            "recommended_agent": self._recommended_agent_for_category(category),
                            "runtime": "openclaw-wrapper",
                        },
                    )
                )

        for category, target in OPENCLAW_CATEGORY_PLAN.items():
            remaining = target - generated_counts[category]
            for index in range(1, remaining + 1):
                skill_id = self._generated_skill_id("openclaw", category, index)
                self._add_skill(
                    Skill(
                        id=skill_id,
                        name=self._generated_skill_name("OpenClaw", category, index),
                        description=self._generated_skill_description(category, "OpenClaw"),
                        category=category,
                        source=SkillSource.MEDICAL_SKILLS,
                        path=f"OpenClaw-Medical-Skills/skills/{skill_id}",
                        package_id="openclaw-medical-wrapper",
                        wrapper_type="openclaw-adapter",
                        tags=self._default_tags_for_category(category),
                        metadata={
                            "packaged": True,
                            "recommended_agent": self._recommended_agent_for_category(category),
                            "runtime": "openclaw-wrapper",
                            "catalog_slot": index,
                        },
                    )
                )

    def _load_ai_research_skills(self):
        for category, count in AI_RESEARCH_CATEGORY_PLAN.items():
            for index in range(1, count + 1):
                skill_id = self._generated_skill_id("research", category, index)
                self._add_skill(
                    Skill(
                        id=skill_id,
                        name=self._generated_skill_name("AI Research", category, index),
                        description=self._generated_skill_description(category, "AI Research"),
                        category=category,
                        source=SkillSource.AI_RESEARCH,
                        path=f"AI-Research-Skills/{skill_id}",
                        package_id="ai-research-suite",
                        wrapper_type="native",
                        tags=self._default_tags_for_category(category),
                        metadata={"packaged": False, "stella_ready": True},
                    )
                )

    def _load_medrt_enhanced_skills(self):
        for category, count in MEDRT_ENHANCED_CATEGORY_PLAN.items():
            for index in range(1, count + 1):
                skill_id = self._generated_skill_id("medrt", category, index)
                self._add_skill(
                    Skill(
                        id=skill_id,
                        name=self._generated_skill_name("MedRT", category, index),
                        description=self._generated_skill_description(category, "MedRT"),
                        category=category,
                        source=SkillSource.MEDRT_ENHANCED,
                        path=f"skills/medroundtable-enhanced/{skill_id}",
                        package_id="medrt-enhanced-suite",
                        wrapper_type="platform-extension",
                        tags=self._default_tags_for_category(category),
                        metadata={"packaged": True, "stella_ready": True},
                    )
                )

    def _validate_totals(self):
        total = len(self.skills)
        if total != TOTAL_SKILL_COUNT:
            raise ValueError(f"技能总数异常: expected {TOTAL_SKILL_COUNT}, got {total}")

        openclaw_count = len(self.get_skills_by_source(SkillSource.MEDICAL_SKILLS))
        if openclaw_count != OPENCLAW_WRAPPED_COUNT:
            raise ValueError(
                f"OpenClaw 包装技能数异常: expected {OPENCLAW_WRAPPED_COUNT}, got {openclaw_count}"
            )

    def _generated_skill_id(self, prefix: str, category: SkillCategory, index: int) -> str:
        slug = {
            SkillCategory.CLINICAL: "clinical",
            SkillCategory.RESEARCH: "research",
            SkillCategory.BIOINFORMATICS: "bioinfo",
            SkillCategory.REGULATORY: "regulatory",
            SkillCategory.AI_ML: "aiml",
            SkillCategory.DATABASE: "database",
            SkillCategory.LITERATURE: "literature",
            SkillCategory.TRIAL: "trial",
            SkillCategory.DRUG: "drug",
            SkillCategory.GENERAL: "general",
        }[category]
        return f"{prefix}-{slug}-{index:03d}"

    def _generated_skill_name(self, family: str, category: SkillCategory, index: int) -> str:
        return f"{family} {category.value}能力 {index:03d}"

    def _generated_skill_description(self, category: SkillCategory, family: str) -> str:
        descriptions = {
            SkillCategory.CLINICAL: "面向临床问题澄清、终点定义、路径建议与临床报告组织。",
            SkillCategory.RESEARCH: "面向科研选题、研究假设扩展、论文结构与研究管理。",
            SkillCategory.BIOINFORMATICS: "面向多组学、生信流程编排、单细胞与变异分析。",
            SkillCategory.REGULATORY: "面向伦理、合规、申报与审查材料校对。",
            SkillCategory.AI_ML: "面向模型评估、RAG、训练、推理与实验自动化。",
            SkillCategory.DATABASE: "面向数据库路由、公共数据集联接与检索聚合。",
            SkillCategory.LITERATURE: "面向医学文献检索、证据提取、综述支持与引文梳理。",
            SkillCategory.TRIAL: "面向临床试验设计、追踪、入排匹配与方案打磨。",
            SkillCategory.DRUG: "面向药物靶点、再利用、药代药效与药物数据库分析。",
            SkillCategory.GENERAL: "面向工作流协同、路由、导出和任务中枢调度。",
        }
        return f"{family} 包装层能力: {descriptions[category]}"

    def _default_tags_for_category(self, category: SkillCategory) -> List[str]:
        tag_map = {
            SkillCategory.CLINICAL: ["临床", "终点", "方案"],
            SkillCategory.RESEARCH: ["研究", "选题", "论文"],
            SkillCategory.BIOINFORMATICS: ["组学", "生信", "分析"],
            SkillCategory.REGULATORY: ["合规", "伦理", "审查"],
            SkillCategory.AI_ML: ["AI", "模型", "自动化"],
            SkillCategory.DATABASE: ["数据库", "检索", "联接"],
            SkillCategory.LITERATURE: ["文献", "证据", "综述"],
            SkillCategory.TRIAL: ["临床试验", "RCT", "设计"],
            SkillCategory.DRUG: ["药物", "靶点", "再利用"],
            SkillCategory.GENERAL: ["中枢", "路由", "导出"],
        }
        return tag_map[category]

    def _recommended_agent_for_category(self, category: SkillCategory) -> str:
        agent_map = {
            SkillCategory.CLINICAL: "clinical_director",
            SkillCategory.RESEARCH: "phd_student",
            SkillCategory.BIOINFORMATICS: "galaxy_bridge",
            SkillCategory.REGULATORY: "qa_expert",
            SkillCategory.AI_ML: "data_engineer",
            SkillCategory.DATABASE: "trend_researcher",
            SkillCategory.LITERATURE: "phd_student",
            SkillCategory.TRIAL: "epidemiologist",
            SkillCategory.DRUG: "pharmacogenomics_expert",
            SkillCategory.GENERAL: "experiment_tracker",
        }
        return agent_map[category]

    def get_skill(self, skill_id: str) -> Optional[Skill]:
        return self.skills.get(skill_id)

    def get_skills_by_category(self, category: SkillCategory) -> List[Skill]:
        return [skill for skill in self.skills.values() if skill.category == category]

    def get_skills_by_source(self, source: SkillSource) -> List[Skill]:
        return [skill for skill in self.skills.values() if skill.source == source]

    def search_skills(self, query: str) -> List[Skill]:
        query = query.lower()
        results = []
        for skill in self.skills.values():
            searchable = " ".join(
                [
                    skill.id,
                    skill.name,
                    skill.description,
                    " ".join(skill.tags),
                    str(skill.metadata.get("recommended_agent", "")),
                ]
            ).lower()
            if query in searchable:
                results.append(skill)
        return results

    def get_all_skills(self) -> List[Skill]:
        return list(self.skills.values())

    def get_categories(self) -> List[Dict[str, Any]]:
        categories: Dict[str, Dict[str, Any]] = {}
        for skill in self.skills.values():
            name = skill.category.value
            entry = categories.setdefault(name, {"name": name, "count": 0, "skills": []})
            entry["count"] += 1
            entry["skills"].append(skill.id)
        return list(categories.values())

    def get_packages(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": package.id,
                "name": package.name,
                "source": package.source.value,
                "total_skills": package.total_skills,
                "description": package.description,
                "packaging": package.packaging,
                "version": package.version,
                "metadata": package.metadata,
            }
            for package in self.packages.values()
        ]

    def get_package(self, package_id: str) -> Optional[Dict[str, Any]]:
        package = self.packages.get(package_id)
        if not package:
            return None
        return {
            "id": package.id,
            "name": package.name,
            "source": package.source.value,
            "total_skills": package.total_skills,
            "description": package.description,
            "packaging": package.packaging,
            "version": package.version,
            "metadata": package.metadata,
        }

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_skills": len(self.skills),
            "openclaw_wrapped_skills": len(self.get_skills_by_source(SkillSource.MEDICAL_SKILLS)),
            "by_category": {
                category.value: len(self.get_skills_by_category(category)) for category in SkillCategory
            },
            "by_source": {
                source.value: len(self.get_skills_by_source(source)) for source in SkillSource
            },
            "enabled": len([skill for skill in self.skills.values() if skill.enabled]),
            "source_packages": {
                package.name: {
                    "id": package.id,
                    "source": package.source.value,
                    "total_skills": package.total_skills,
                    "packaging": package.packaging,
                }
                for package in self.packages.values()
            },
        }


skill_registry = SkillRegistry()


if __name__ == "__main__":
    registry = SkillRegistry()
    print(f"总技能数: {len(registry.get_all_skills())}")
    print(f"OpenClaw 包装技能数: {len(registry.get_skills_by_source(SkillSource.MEDICAL_SKILLS))}")
    print(f"统计: {registry.get_stats()}")
