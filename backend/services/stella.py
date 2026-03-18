"""
STELLA 多智能体编排层

Manager -> Dev -> Critic
用于把 MedRoundTable 的 14 位专家与 997 项技能组织为稳定的执行蓝图。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from skills.registry import SkillCategory, skill_registry


@dataclass(frozen=True)
class StellaRoleProfile:
    id: str
    name: str
    responsibility: str
    mapped_agents: List[str]
    outputs: List[str]


STELLA_ROLES = [
    StellaRoleProfile(
        id="manager",
        name="Manager",
        responsibility="定义研究目标、拆分执行阶段、路由技能与专家。",
        mapped_agents=["clinical_director", "phd_student", "experiment_tracker"],
        outputs=["任务蓝图", "阶段目标", "技能路由建议"],
    ),
    StellaRoleProfile(
        id="dev",
        name="Dev",
        responsibility="组织领域专家与技能链路，产出方案、分析与可交付物。",
        mapped_agents=[
            "epidemiologist",
            "statistician",
            "research_nurse",
            "pharmacogenomics_expert",
            "gwas_expert",
            "single_cell_analyst",
            "galaxy_bridge",
            "data_engineer",
        ],
        outputs=["研究设计", "分析计划", "数据库/技能调用链"],
    ),
    StellaRoleProfile(
        id="critic",
        name="Critic",
        responsibility="对输出进行质量、偏差、可发表性与合规审查。",
        mapped_agents=["qa_expert", "trend_researcher", "ux_researcher"],
        outputs=["质量门禁", "风险提示", "改进建议"],
    ),
]

STAGE_CATEGORY_MAP = {
    "literature_review": [SkillCategory.LITERATURE, SkillCategory.DATABASE, SkillCategory.RESEARCH],
    "study_design": [SkillCategory.TRIAL, SkillCategory.CLINICAL, SkillCategory.RESEARCH],
    "data_analysis": [SkillCategory.BIOINFORMATICS, SkillCategory.DATABASE, SkillCategory.AI_ML],
    "publication": [SkillCategory.LITERATURE, SkillCategory.RESEARCH, SkillCategory.REGULATORY],
    "drug_discovery": [SkillCategory.DRUG, SkillCategory.BIOINFORMATICS, SkillCategory.AI_ML],
    "trial_execution": [SkillCategory.TRIAL, SkillCategory.CLINICAL, SkillCategory.REGULATORY],
}

KEYWORD_CATEGORY_MAP = {
    "文献": SkillCategory.LITERATURE,
    "综述": SkillCategory.LITERATURE,
    "试验": SkillCategory.TRIAL,
    "rct": SkillCategory.TRIAL,
    "队列": SkillCategory.TRIAL,
    "终点": SkillCategory.CLINICAL,
    "生存": SkillCategory.CLINICAL,
    "单细胞": SkillCategory.BIOINFORMATICS,
    "gwas": SkillCategory.BIOINFORMATICS,
    "多组学": SkillCategory.BIOINFORMATICS,
    "药物": SkillCategory.DRUG,
    "药代": SkillCategory.DRUG,
    "数据库": SkillCategory.DATABASE,
    "nhanes": SkillCategory.DATABASE,
    "seer": SkillCategory.DATABASE,
    "charls": SkillCategory.DATABASE,
    "伦理": SkillCategory.REGULATORY,
    "合规": SkillCategory.REGULATORY,
    "ai": SkillCategory.AI_ML,
    "模型": SkillCategory.AI_ML,
}


class StellaService:
    """STELLA 编排服务"""

    def get_architecture(self) -> Dict[str, Any]:
        return {
            "name": "STELLA",
            "pattern": "Manager-Dev-Critic",
            "description": "在 14 位医学科研专家之上增加一层稳定的元编排结构，用于任务拆分、执行和审查。",
            "roles": [
                {
                    "id": role.id,
                    "name": role.name,
                    "responsibility": role.responsibility,
                    "mapped_agents": role.mapped_agents,
                    "outputs": role.outputs,
                }
                for role in STELLA_ROLES
            ],
            "integrations": {
                "skill_marketplace_total": skill_registry.get_stats()["total_skills"],
                "openclaw_wrapped": skill_registry.get_stats()["openclaw_wrapped_skills"],
                "medical_experts": 14,
            },
        }

    def build_workflow(
        self,
        objective: str,
        clinical_question: str,
        research_stage: Optional[str] = None,
        required_outputs: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        required_outputs = required_outputs or []
        constraints = constraints or []
        categories = self._infer_categories(objective, clinical_question, research_stage)
        recommended_skills = self._pick_skills(objective, categories, limit=8)

        return {
            "stella_mode": "manager-dev-critic",
            "manager": self._build_manager_plan(objective, clinical_question, research_stage, categories),
            "dev": self._build_dev_plan(categories, recommended_skills, required_outputs),
            "critic": self._build_critic_plan(categories, constraints),
            "recommended_skills": recommended_skills,
            "quality_gates": self._build_quality_gates(categories),
            "delivery_targets": required_outputs,
        }

    def _infer_categories(
        self, objective: str, clinical_question: str, research_stage: Optional[str]
    ) -> List[SkillCategory]:
        categories: List[SkillCategory] = []
        if research_stage and research_stage in STAGE_CATEGORY_MAP:
            categories.extend(STAGE_CATEGORY_MAP[research_stage])

        haystack = f"{objective} {clinical_question}".lower()
        for keyword, category in KEYWORD_CATEGORY_MAP.items():
            if keyword in haystack and category not in categories:
                categories.append(category)

        if not categories:
            categories = [SkillCategory.LITERATURE, SkillCategory.TRIAL, SkillCategory.CLINICAL]

        return categories

    def _pick_skills(
        self, objective: str, categories: List[SkillCategory], limit: int = 8
    ) -> List[Dict[str, Any]]:
        query_matches = skill_registry.search_skills(objective)[:limit]
        filtered_matches = [skill for skill in query_matches if skill.category in categories]

        if len(filtered_matches) < limit:
            for category in categories:
                for skill in skill_registry.get_skills_by_category(category)[: limit - len(filtered_matches)]:
                    if skill.id not in {item.id for item in filtered_matches}:
                        filtered_matches.append(skill)
                    if len(filtered_matches) >= limit:
                        break
                if len(filtered_matches) >= limit:
                    break

        return [
            {
                "id": skill.id,
                "name": skill.name,
                "category": skill.category.value,
                "source": skill.source.value,
                "wrapper_type": skill.wrapper_type,
                "recommended_agent": skill.metadata.get("recommended_agent"),
                "package_id": skill.package_id,
            }
            for skill in filtered_matches[:limit]
        ]

    def _build_manager_plan(
        self,
        objective: str,
        clinical_question: str,
        research_stage: Optional[str],
        categories: List[SkillCategory],
    ) -> Dict[str, Any]:
        return {
            "lead_role": "manager",
            "mapped_agents": STELLA_ROLES[0].mapped_agents,
            "objective": objective,
            "clinical_question": clinical_question,
            "research_stage": research_stage or "study_design",
            "focus_categories": [category.value for category in categories],
            "actions": [
                "统一研究目标与主要临床问题",
                "拆解阶段交付物并路由给 14 位专家中的相关角色",
                "优先调用 OpenClaw 包装技能补足数据库与分析能力",
            ],
        }

    def _build_dev_plan(
        self,
        categories: List[SkillCategory],
        recommended_skills: List[Dict[str, Any]],
        required_outputs: List[str],
    ) -> Dict[str, Any]:
        specialist_agents: List[str] = []
        for category in categories:
            specialist_agents.extend(self._agents_for_category(category))

        unique_agents = list(dict.fromkeys(STELLA_ROLES[1].mapped_agents + specialist_agents))
        return {
            "lead_role": "dev",
            "mapped_agents": unique_agents,
            "execution_steps": [
                {
                    "phase": "需求转技术任务",
                    "owner": "epidemiologist",
                    "goal": "把临床问题转成可执行研究设计与分析清单",
                },
                {
                    "phase": "技能调用编排",
                    "owner": "data_engineer",
                    "goal": "把 OpenClaw 869 项包装技能与 MedRoundTable 原生能力拼成工作流",
                },
                {
                    "phase": "研究输出生成",
                    "owner": "statistician",
                    "goal": "产出方案、分析、可视化和结构化研究结论",
                },
            ],
            "recommended_skills": recommended_skills,
            "required_outputs": required_outputs,
        }

    def _build_critic_plan(
        self, categories: List[SkillCategory], constraints: List[str]
    ) -> Dict[str, Any]:
        return {
            "lead_role": "critic",
            "mapped_agents": STELLA_ROLES[2].mapped_agents,
            "review_dimensions": [
                "临床合理性",
                "方法学严谨性",
                "数据与模型偏差",
                "伦理与法规合规",
                "期刊级表达与可发表性",
            ],
            "constraints": constraints,
            "priority_checks": self._build_quality_gates(categories),
        }

    def _build_quality_gates(self, categories: List[SkillCategory]) -> List[str]:
        gates = [
            "主要终点和纳入排除标准必须可操作",
            "统计分析路径需要与研究设计一致",
            "涉及患者数据时必须经过隐私和伦理检查",
        ]

        if SkillCategory.BIOINFORMATICS in categories:
            gates.append("组学分析必须给出质控、参数和可复现说明")
        if SkillCategory.TRIAL in categories:
            gates.append("试验设计必须覆盖样本量、随机化和偏倚控制")
        if SkillCategory.DRUG in categories:
            gates.append("药物建议必须注明证据来源与潜在相互作用风险")

        return gates

    def _agents_for_category(self, category: SkillCategory) -> List[str]:
        mapping = {
            SkillCategory.LITERATURE: ["phd_student"],
            SkillCategory.TRIAL: ["epidemiologist", "research_nurse"],
            SkillCategory.CLINICAL: ["clinical_director", "statistician"],
            SkillCategory.BIOINFORMATICS: [
                "pharmacogenomics_expert",
                "gwas_expert",
                "single_cell_analyst",
                "galaxy_bridge",
            ],
            SkillCategory.DRUG: ["pharmacogenomics_expert"],
            SkillCategory.DATABASE: ["trend_researcher", "data_engineer"],
            SkillCategory.RESEARCH: ["experiment_tracker", "phd_student"],
            SkillCategory.AI_ML: ["data_engineer", "qa_expert"],
            SkillCategory.REGULATORY: ["qa_expert", "research_nurse"],
            SkillCategory.GENERAL: ["experiment_tracker"],
        }
        return mapping.get(category, [])


stella_service = StellaService()
