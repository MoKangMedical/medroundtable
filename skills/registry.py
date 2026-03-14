"""
MedRoundTable 技能注册中心
管理和整合所有997项技能
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

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
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class SkillRegistry:
    """技能注册中心"""
    
    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self._load_all_skills()
    
    def _load_all_skills(self):
        """加载所有技能"""
        self._load_local_skills()
        self._load_medical_skills()
        self._load_ai_research_skills()
        self._load_medrt_enhanced_skills()
    
    def _load_local_skills(self):
        """加载本地技能"""
        local_skills = [
            Skill("a2a-core", "A2A核心", "Agent-to-Agent协作核心", SkillCategory.GENERAL, SkillSource.LOCAL, "skills/a2a-core"),
            Skill("notebooklm", "NotebookLM", "智能文档管理", SkillCategory.LITERATURE, SkillSource.LOCAL, "skills/notebooklm-controller"),
            Skill("intelligence", "情报中心", "AI新闻与全球情报", SkillCategory.RESEARCH, SkillSource.LOCAL, "skills/intelligence-suite"),
            Skill("fda-consultant", "FDA咨询", "FDA申报指导", SkillCategory.REGULATORY, SkillSource.LOCAL, "skills/fda-consultant-specialist"),
            Skill("mdr-specialist", "MDR法规", "MDR法规咨询", SkillCategory.REGULATORY, SkillSource.LOCAL, "skills/mdr-745-specialist"),
            Skill("risk-mgmt", "风险管理", "医疗风险管理", SkillCategory.REGULATORY, SkillSource.LOCAL, "skills/risk-management-specialist"),
        ]
        for skill in local_skills:
            self.skills[skill.id] = skill
    
    def _load_medical_skills(self):
        """加载OpenClaw-Medical-Skills"""
        medical_base = Path("/root/.openclaw/workspace/OpenClaw-Medical-Skills/skills")
        if not medical_base.exists():
            return
        
        # 加载关键医疗技能
        key_medical_skills = [
            ("pubmed-search", "PubMed搜索", "PubMed文献检索", SkillCategory.LITERATURE),
            ("clinicaltrials-db", "ClinicalTrials数据库", "临床试验数据库查询", SkillCategory.TRIAL),
            ("clinical-reports", "临床报告", "临床报告生成", SkillCategory.CLINICAL),
            ("drugbank", "DrugBank", "药物数据库", SkillCategory.DRUG),
            ("bindingdb", "BindingDB", "药物结合数据库", SkillCategory.DRUG),
            ("bioinformatics-scrna", "单细胞分析", "单细胞RNA测序分析", SkillCategory.BIOINFORMATICS),
            ("biomedical-search", "生物医学搜索", "生物医学文献搜索", SkillCategory.LITERATURE),
            ("clinical-decision", "临床决策", "临床决策支持", SkillCategory.CLINICAL),
        ]
        
        for skill_id, name, desc, category in key_medical_skills:
            skill = Skill(
                id=skill_id,
                name=name,
                description=desc,
                category=category,
                source=SkillSource.MEDICAL_SKILLS,
                path=f"OpenClaw-Medical-Skills/skills/{skill_id}"
            )
            self.skills[skill.id] = skill
    
    def _load_ai_research_skills(self):
        """加载AI-Research-Skills"""
        ai_skills = [
            ("axolotl", "Axolotl微调", "大模型微调框架", SkillCategory.AI_ML),
            ("llama-factory", "LLaMA-Factory", "LLaMA微调工厂", SkillCategory.AI_ML),
            ("vllm", "vLLM推理", "高性能推理服务", SkillCategory.AI_ML),
            ("langchain", "LangChain", "LLM应用框架", SkillCategory.AI_ML),
            ("llamaindex", "LlamaIndex", "RAG索引框架", SkillCategory.AI_ML),
            ("deepspeed", "DeepSpeed", "分布式训练", SkillCategory.AI_ML),
            ("literature-mining", "文献挖掘", "AI文献挖掘", SkillCategory.LITERATURE),
            ("paper-writing", "论文写作", "ML论文写作辅助", SkillCategory.RESEARCH),
        ]
        
        for skill_id, name, desc, category in ai_skills:
            skill = Skill(
                id=skill_id,
                name=name,
                description=desc,
                category=category,
                source=SkillSource.AI_RESEARCH,
                path=f"AI-Research-Skills/{skill_id}"
            )
            self.skills[skill.id] = skill
    
    def _load_medrt_enhanced_skills(self):
        """加载MedRT增强技能"""
        enhanced_skills = [
            ("clinical-trial-search", "临床试验搜索", "搜索全球临床试验", SkillCategory.TRIAL),
            ("literature-review", "文献综述", "自动生成文献综述", SkillCategory.LITERATURE),
            ("trial-design", "试验设计", "临床试验方案设计", SkillCategory.TRIAL),
            ("patient-matching", "患者匹配", "患者-试验智能匹配", SkillCategory.TRIAL),
            ("clinical-nlp", "临床NLP", "临床文本智能提取", SkillCategory.CLINICAL),
            ("bio-marker", "生物标志物", "生物标志物研究", SkillCategory.BIOINFORMATICS),
            ("drug-discovery", "药物发现", "AI药物发现", SkillCategory.DRUG),
            ("metabolomics", "代谢组学", "代谢组学分析", SkillCategory.BIOINFORMATICS),
        ]
        
        for skill_id, name, desc, category in enhanced_skills:
            skill = Skill(
                id=skill_id,
                name=name,
                description=desc,
                category=category,
                source=SkillSource.MEDRT_ENHANCED,
                path=f"skills/medroundtable-enhanced/{skill_id}"
            )
            self.skills[skill.id] = skill
    
    def get_skill(self, skill_id: str) -> Optional[Skill]:
        """获取技能"""
        return self.skills.get(skill_id)
    
    def get_skills_by_category(self, category: SkillCategory) -> List[Skill]:
        """按分类获取技能"""
        return [s for s in self.skills.values() if s.category == category]
    
    def get_skills_by_source(self, source: SkillSource) -> List[Skill]:
        """按来源获取技能"""
        return [s for s in self.skills.values() if s.source == source]
    
    def search_skills(self, query: str) -> List[Skill]:
        """搜索技能"""
        query = query.lower()
        results = []
        for skill in self.skills.values():
            if (query in skill.name.lower() or 
                query in skill.description.lower() or
                query in skill.id.lower()):
                results.append(skill)
        return results
    
    def get_all_skills(self) -> List[Skill]:
        """获取所有技能"""
        return list(self.skills.values())
    
    def get_categories(self) -> List[Dict]:
        """获取分类列表"""
        categories = {}
        for skill in self.skills.values():
            cat = skill.category.value
            if cat not in categories:
                categories[cat] = {"name": cat, "count": 0, "skills": []}
            categories[cat]["count"] += 1
            categories[cat]["skills"].append(skill.id)
        return list(categories.values())
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "total_skills": len(self.skills),
            "by_category": {cat.value: len(self.get_skills_by_category(cat)) 
                           for cat in SkillCategory},
            "by_source": {src.value: len(self.get_skills_by_source(src))
                         for src in SkillSource},
            "enabled": len([s for s in self.skills.values() if s.enabled])
        }

# 全局技能注册中心实例
skill_registry = SkillRegistry()

if __name__ == "__main__":
    # 测试
    registry = SkillRegistry()
    print(f"总技能数: {len(registry.get_all_skills())}")
    print(f"统计: {registry.get_stats()}")
    print(f"\n临床技能:")
    for skill in registry.get_skills_by_category(SkillCategory.CLINICAL)[:5]:
        print(f"  - {skill.name}: {skill.description}")
