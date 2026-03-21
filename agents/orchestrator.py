import asyncio
import uuid
import traceback
from typing import List, Dict, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
import json
import re

from backend.models import A2AMessage, AgentRole, MessageType, RoundTable, RoundTableStatus
from agents.prompts import AGENT_PROFILES, DISCUSSION_STAGES
from agents.llm_client import llm_client
from backend.citation_manager import citation_manager


@dataclass
class Agent:
    """Agent 基类 - 使用真实 LLM API"""
    role: AgentRole
    name: str
    avatar: str
    system_prompt: str
    expertise: List[str]
    
    async def generate_response(
        self, 
        message: A2AMessage, 
        context: List[A2AMessage],
        stage: str,
        roundtable=None
    ) -> str:
        """使用 LLM API 生成响应"""
        
        # 构建完整的上下文提示
        context_prompt = self._build_context_prompt(message, context, stage, roundtable)
        
        # 调用 LLM API
        try:
            response = await llm_client.generate_response(
                system_prompt=self.system_prompt,
                user_prompt=context_prompt,
                temperature=0.7,
                max_tokens=2000
            )
            return response
        except Exception as e:
            print(f"LLM 调用失败，使用备用响应: {e}")
            return self._fallback_response(message, context, stage)
    
    def _build_context_prompt(self, message: A2AMessage, context: List[A2AMessage], stage: str, roundtable=None) -> str:
        """构建上下文提示"""
        
        # 尝试从 message metadata 获取（优先）
        clinical_question = ""
        roundtable_title = ""
        
        if hasattr(message, 'metadata') and message.metadata:
            clinical_question = message.metadata.get('clinical_question', '')
            roundtable_title = message.metadata.get('title', '')
        
        # 如果从 message 没获取到，尝试从 context
        if not clinical_question:
            for msg in context:
                if hasattr(msg, 'metadata') and msg.metadata:
                    if not clinical_question and 'clinical_question' in msg.metadata:
                        clinical_question = msg.metadata['clinical_question']
                    if not roundtable_title and 'title' in msg.metadata:
                        roundtable_title = msg.metadata['title']
                    if clinical_question and roundtable_title:
                        break
        
        # 如果传入了 roundtable 对象，直接从对象获取（最可靠）
        if roundtable:
            if not clinical_question:
                clinical_question = roundtable.clinical_question
            if not roundtable_title:
                roundtable_title = roundtable.title

        requested_outputs = []
        request_text = f"{clinical_question}\n{message.content}"
        deliverable_keywords = {
            "样本量": ["样本量", "效能", "power", "把握度"],
            "主要终点": ["终点", "primary endpoint", "主要指标"],
            "CRF字段": ["crf", "字段", "表格", "变量", "采集表"],
            "访视表": ["访视", "时间窗", "随访"],
            "SOP": ["sop", "操作手册", "流程"],
            "风险点": ["风险", "不良事件", "偏倚", "混杂", "脱落"],
            "交付物": ["交付物", "输出", "里程碑", "下一步"],
        }
        lowered_request = request_text.lower()
        for label, keywords in deliverable_keywords.items():
            if any(keyword in lowered_request for keyword in keywords):
                requested_outputs.append(label)
        
        prompt = f"""你正在参加一个医学科研圆桌讨论。当前阶段: {stage}

你的角色: {self.name}
你的专长: {', '.join(self.expertise)}

=== 研究基本信息 ===
研究标题: {roundtable_title or "待讨论的研究项目"}
临床问题: {clinical_question or "需要讨论的临床问题"}

=== 之前的讨论记录 ===
"""
        
        # 添加最近5条消息作为上下文
        recent_messages = context[-5:] if len(context) > 5 else context
        for msg in recent_messages:
            role_name = msg.from_role.value if hasattr(msg.from_role, 'value') else str(msg.from_role)
            prompt += f"\n{role_name}: {msg.content[:200]}...\n" if len(msg.content) > 200 else f"\n{role_name}: {msg.content}\n"
        
        recent_peer_views = []
        for msg in reversed(recent_messages):
            role_name = msg.from_role.value if hasattr(msg.from_role, 'value') else str(msg.from_role)
            if role_name not in {self.role.value, "user", "system"}:
                recent_peer_views.append((role_name, msg.content[:180]))
            if len(recent_peer_views) == 2:
                break

        prompt += f"""
=== 当前消息 ===
来自: {message.from_role.value if hasattr(message.from_role, 'value') else str(message.from_role)}
内容: {message.content}

=== 你的任务 ===
请根据你的专业角色、研究的基本信息（研究标题和临床问题）以及讨论上下文，给出专业、详细的回应。
要求:
1. 使用中文回答，内容必须紧扣上述"临床问题"
2. 体现你的专业视角，给出具体可行的建议，避免空泛定义或重复背景
3. 如果提到疾病名称、干预措施或终点指标，请使用临床问题中提到的具体内容
4. 如果有不同意见，请礼貌提出；如果同意，请补充你的专业建议
5. 如果用户要求“表格/字段/样本量/终点/SOP”，请直接输出结构化清单或数字，不要只说原则
6. 请至少回应一位前序专家的观点，说明你是补充、修正还是质疑
7. 优先给出样本量、字段、终点、风险点、交付物，而不是复述概念
8. 不要复述阶段任务原文，不要把提示词当作回答内容，也不要用“如果你要我可以继续”收尾
9. 避免写“尊敬的各位专家”“下面我汇报”等空泛开场，直接进入问题本身
"""

        if recent_peer_views:
            prompt += "\n=== 你需要回应的前序观点 ===\n"
            for role_name, content in recent_peer_views:
                prompt += f"- {role_name}: {content}\n"

        if requested_outputs:
            prompt += "\n=== 本轮必须覆盖的交付物 ===\n"
            for output in requested_outputs:
                prompt += f"- {output}\n"

        prompt += """

请给出你的回应:"""
        
        return prompt
    
    def _fallback_response(self, message, context, stage):
        """备用响应（当 LLM 失败时使用）- 支持全部14个Agent"""
        responses = {
            # 核心临床团队
            AgentRole.CLINICAL_DIRECTOR: "从临床角度来看，这个研究方向很有价值。我建议我们进一步讨论具体的实施方案。",
            AgentRole.PHD_STUDENT: "我会记录这个要点，并查找相关文献支持。",
            AgentRole.EPIDEMIOLOGIST: "从方法学角度，我建议考虑选择偏倚的控制和样本量计算。",
            AgentRole.STATISTICIAN: "从统计学角度，我们需要明确主要终点和统计方法。",
            AgentRole.RESEARCH_NURSE: "从执行角度，我们需要考虑实际操作的可行性和质量控制。",
            
            # 生物信息学套件
            AgentRole.PHARMACOGENOMICS_EXPERT: "从药物基因组学角度，建议考虑基因检测对药物治疗效果的影响，以及个体化用药的可能性。",
            AgentRole.GWAS_EXPERT: "从GWAS分析角度，建议收集足够的样本量进行全基因组关联分析，以发现潜在的遗传风险位点。",
            AgentRole.SINGLE_CELL_ANALYST: "从单细胞分析角度，建议考虑采用单细胞测序技术深入研究细胞异质性和分子机制。",
            AgentRole.GALAXY_BRIDGE: "从生物信息学工具角度，我可以协调Galaxy平台上的8000+工具进行多组学数据分析。",
            
            # 专业研究Agent
            AgentRole.UX_RESEARCHER: "从用户体验角度，建议优化数据采集流程，确保研究人员能够高效使用平台工具。",
            AgentRole.DATA_ENGINEER: "从数据工程角度，建议建立标准化的数据管道，确保多源数据的质量和一致性。",
            AgentRole.TREND_RESEARCHER: "从科研趋势角度，这个研究方向符合当前领域热点，具有较高的创新性和发表潜力。",
            AgentRole.EXPERIMENT_TRACKER: "从项目管理角度，建议制定详细的里程碑计划，确保各阶段按时交付。",
            AgentRole.QA_EXPERT: "从质量控制角度，建议建立严格的质量检查点，确保研究结果的可靠性和可重复性。"
        }
        return responses.get(self.role, "我同意上述观点，会从我的专业角度提供支持。")


class A2AOrchestrator:
    """A2A 协调器 - 管理圆桌讨论流程"""
    
    def __init__(self):
        self.agents: Dict[AgentRole, Agent] = {}
        self.sessions: Dict[str, RoundTable] = {}
        self.message_callbacks: List[Callable] = []
        self._init_agents()
    
    def _init_agents(self):
        """初始化所有Agent"""
        for role, profile in AGENT_PROFILES.items():
            self.agents[AgentRole(role)] = Agent(
                role=AgentRole(role),
                name=profile["name"],
                avatar=profile["avatar"],
                system_prompt=profile["system_prompt"],
                expertise=profile["expertise"]
            )
    
    def register_message_callback(self, callback: Callable):
        """注册消息回调函数"""
        if callback not in self.message_callbacks:
            self.message_callbacks.append(callback)

    def _get_requested_roles(self, clinical_question: str) -> List[AgentRole]:
        """根据用户问题补充需要提前介入的专家角色。"""
        lowered = (clinical_question or "").lower()
        requested_roles: List[AgentRole] = []
        keyword_map = [
            (AgentRole.STATISTICIAN, ["样本量", "效能", "power", "终点", "统计", "sap"]),
            (AgentRole.RESEARCH_NURSE, ["crf", "字段", "表格", "变量", "访视", "sop", "流程"]),
            (AgentRole.EPIDEMIOLOGIST, ["偏倚", "混杂", "纳入", "排除", "研究设计"]),
            (AgentRole.GALAXY_BRIDGE, ["多组学", "workflow", "单细胞", "gwas", "基因"]),
        ]
        for role, keywords in keyword_map:
            if any(keyword in lowered for keyword in keywords):
                requested_roles.append(role)
        return requested_roles

    def _build_stage_instruction(self, stage_config: Dict[str, str], stage: str, clinical_question: str) -> str:
        """把阶段说明压成可执行指令，避免 agent 直接复述题目。"""
        stage_name = stage_config.get("description", stage)
        base_prompt = stage_config.get("prompt", "请发表你的观点")
        requested_roles = self._get_requested_roles(clinical_question)
        deliverables = []
        if AgentRole.STATISTICIAN in requested_roles:
            deliverables.append("具体样本量、主要终点和统计骨架")
        if AgentRole.RESEARCH_NURSE in requested_roles:
            deliverables.append("CRF 字段、访视表和执行流程")
        if AgentRole.EPIDEMIOLOGIST in requested_roles:
            deliverables.append("纳排标准与偏倚控制")
        if AgentRole.GALAXY_BRIDGE in requested_roles:
            deliverables.append("组学分析流程与工具链")

        instruction = f"当前阶段是“{stage_name}”。请直接给本阶段最重要的可执行结论，不要复述任务说明。"
        if deliverables:
            instruction += f" 本轮用户已经明确要：{'；'.join(deliverables)}。"
        instruction += f" 需要推进的核心事项：{base_prompt.replace(chr(10), ' ')}"
        return instruction

    def unregister_message_callback(self, callback: Callable):
        """解除注册消息回调函数"""
        try:
            self.message_callbacks.remove(callback)
        except ValueError:
            pass

    def _infer_requested_outputs(self, text: str) -> List[str]:
        lowered = (text or "").lower()
        mapping = [
            ("主要终点", ["终点", "endpoint", "指标"]),
            ("样本量", ["样本量", "效能", "power", "把握度"]),
            ("CRF字段", ["crf", "字段", "变量", "表格", "采集表"]),
            ("访视表", ["访视", "随访", "时间窗"]),
            ("风险点", ["风险", "不良事件", "偏倚", "混杂", "脱落"]),
            ("交付物", ["交付物", "输出", "里程碑", "下一步"]),
        ]
        return [label for label, keywords in mapping if any(keyword in lowered for keyword in keywords)]

    def _get_latest_stage(self, roundtable: RoundTable) -> str:
        for message in reversed(roundtable.messages):
            stage = (message.metadata or {}).get("stage")
            if stage:
                return stage
        return "problem_presentation"

    def _select_kickoff_roles(self, roundtable: RoundTable) -> List[AgentRole]:
        ordered_roles = [AgentRole.CLINICAL_DIRECTOR]
        ordered_roles.extend(self._get_requested_roles(roundtable.clinical_question))
        ordered_roles.extend([
            AgentRole.PHD_STUDENT,
            AgentRole.EPIDEMIOLOGIST,
            AgentRole.STATISTICIAN,
            AgentRole.RESEARCH_NURSE,
        ])

        if self._requires_bioinformatics_stage(roundtable.clinical_question):
            ordered_roles.extend([
                AgentRole.GALAXY_BRIDGE,
                AgentRole.DATA_ENGINEER,
            ])
        else:
            ordered_roles.extend([
                AgentRole.TREND_RESEARCHER,
                AgentRole.EXPERIMENT_TRACKER,
            ])

        deduped_roles: List[AgentRole] = []
        for role in ordered_roles:
            if role not in deduped_roles:
                deduped_roles.append(role)
        return deduped_roles[:5]

    def _get_stage_roles(
        self,
        stage: str,
        roundtable: RoundTable,
        extra_text: str = ""
    ) -> List[AgentRole]:
        """返回某个阶段应当参与的完整角色集合，而不是只保留 2-3 个默认专家。"""
        stage_config = DISCUSSION_STAGES.get(stage, {})
        ordered_roles: List[AgentRole] = []

        leader_value = stage_config.get("leader")
        if leader_value in AgentRole._value2member_map_:
            ordered_roles.append(AgentRole(leader_value))

        for role in stage_config.get("participants", []):
            if role in AgentRole._value2member_map_:
                ordered_roles.append(AgentRole(role))

        requested_roles = self._get_requested_roles(
            f"{roundtable.clinical_question}\n{extra_text}".strip()
        )
        ordered_roles.extend(requested_roles)

        stage_support_roles = {
            "problem_presentation": [
                AgentRole.STATISTICIAN,
                AgentRole.RESEARCH_NURSE,
                AgentRole.TREND_RESEARCHER,
            ],
            "literature_review": [
                AgentRole.TREND_RESEARCHER,
                AgentRole.QA_EXPERT,
            ],
            "study_design": [
                AgentRole.RESEARCH_NURSE,
                AgentRole.TREND_RESEARCHER,
                AgentRole.UX_RESEARCHER,
            ],
            "bioinformatics_plan": [
                AgentRole.PHARMACOGENOMICS_EXPERT,
                AgentRole.GWAS_EXPERT,
                AgentRole.SINGLE_CELL_ANALYST,
                AgentRole.GALAXY_BRIDGE,
                AgentRole.DATA_ENGINEER,
            ],
            "statistical_plan": [
                AgentRole.RESEARCH_NURSE,
                AgentRole.QA_EXPERT,
                AgentRole.DATA_ENGINEER,
            ],
            "crf_design": [
                AgentRole.EXPERIMENT_TRACKER,
                AgentRole.UX_RESEARCHER,
                AgentRole.QA_EXPERT,
            ],
            "execution_plan": [
                AgentRole.DATA_ENGINEER,
                AgentRole.QA_EXPERT,
                AgentRole.EXPERIMENT_TRACKER,
            ],
            "quality_review": [
                AgentRole.EXPERIMENT_TRACKER,
                AgentRole.TREND_RESEARCHER,
                AgentRole.UX_RESEARCHER,
                AgentRole.QA_EXPERT,
            ],
            "consensus": [
                AgentRole.EXPERIMENT_TRACKER,
                AgentRole.TREND_RESEARCHER,
                AgentRole.PHD_STUDENT,
            ],
        }
        ordered_roles.extend(stage_support_roles.get(stage, []))

        deduped_roles: List[AgentRole] = []
        for role in ordered_roles:
            if role not in deduped_roles:
                deduped_roles.append(role)

        return deduped_roles

    def _get_stage_sequence(self, roundtable: RoundTable) -> List[str]:
        stages = [
            "problem_presentation",
            "literature_review",
            "study_design",
            "bioinformatics_plan",
            "statistical_plan",
            "crf_design",
            "execution_plan",
            "quality_review",
            "consensus",
        ]
        return stages

    def _get_next_stage(self, roundtable: RoundTable) -> str:
        stages = self._get_stage_sequence(roundtable)
        latest_stage = self._get_latest_stage(roundtable)
        if latest_stage not in stages:
            return stages[0]
        latest_index = stages.index(latest_stage)
        if latest_index >= len(stages) - 1:
            return stages[-1]
        return stages[latest_index + 1]

    def _infer_requested_stage(self, user_content: str) -> Optional[str]:
        lowered = (user_content or "").lower()
        stage_patterns = [
            ("problem_presentation", ["问题识别", "立项", "研究问题", "主问题", "go/no-go", "值得做"]),
            ("literature_review", ["文献回顾", "文献", "证据表", "检索", "综述", "指南"]),
            ("study_design", ["研究设计", "纳排", "纳入排除", "偏倚控制", "方案骨架"]),
            ("bioinformatics_plan", ["生信", "组学", "gwas", "单细胞", "转录组", "多组学", "workflow"]),
            ("statistical_plan", ["数据分析", "统计分析", "样本量", "sap", "敏感性分析", "分析集"]),
            ("crf_design", ["crf", "字段表", "访视表"]),
            ("execution_plan", ["执行计划", "里程碑", "排期", "试运行", "培训"]),
            ("quality_review", ["质控", "qa", "复核", "返工", "一致性"]),
            ("consensus", ["总结", "最终报告", "形成报告", "执行摘要", "共识"]),
        ]
        for stage, markers in stage_patterns:
            if any(marker in lowered for marker in markers):
                return stage
        return None

    def _build_kickoff_placeholder(self, roundtable: RoundTable) -> str:
        requested_outputs = self._infer_requested_outputs(roundtable.clinical_question)
        if not requested_outputs:
            requested_outputs = ["主要终点", "样本量", "CRF字段", "风险点"]

        kickoff_roles = self._select_kickoff_roles(roundtable)
        role_labels = " -> ".join(self.agents[role].name for role in kickoff_roles)
        output_lines = "\n".join(
            f"{index}. {label}" for index, label in enumerate(requested_outputs[:4], start=1)
        )

        return f"""我先把首轮会诊的目标钉住，不重复背景。

本轮优先收这几项可交付内容：
{output_lines}

先由 {role_labels} 依次补齐；每位专家都直接给数字、字段、时间窗、风险点或下一步动作。"""

    def _build_continue_prompt(
        self,
        roundtable: RoundTable,
        user_content: str,
        target_stage: Optional[str] = None
    ) -> str:
        latest_stage = self._get_latest_stage(roundtable)
        target_stage = target_stage or latest_stage
        stage_description = DISCUSSION_STAGES.get(target_stage, {}).get("description", target_stage)
        requested_outputs = self._infer_requested_outputs(
            f"{roundtable.clinical_question}\n{user_content}"
        )
        if not requested_outputs:
            requested_outputs = ["主要终点", "样本量", "CRF字段", "访视表", "风险点", "交付物"]

        output_lines = "\n".join(f"- {item}" for item in requested_outputs[:6])
        return f"""用户要求继续推进当前讨论。不要重复背景，不要解释讨论流程，直接把内容往下做实。

上一阶段：{latest_stage}
当前推进阶段：{target_stage}（{stage_description}）
本轮优先补这几项：
{output_lines}

请直接回应前面专家的判断，并给出你负责的具体数字、字段、时间窗、风险点或下一步交付物。"""

    def _select_continue_roles(
        self,
        roundtable: RoundTable,
        user_content: str,
        target_stage: Optional[str] = None
    ) -> List[AgentRole]:
        latest_stage = target_stage or self._get_latest_stage(roundtable)
        stage_roles = self._get_stage_roles(latest_stage, roundtable, user_content)
        if stage_roles:
            return stage_roles[:5]
        return [AgentRole.CLINICAL_DIRECTOR, AgentRole.STATISTICIAN, AgentRole.RESEARCH_NURSE]

    def _requires_bioinformatics_stage(self, clinical_question: str) -> bool:
        lowered = (clinical_question or "").lower()
        return any(
            keyword in lowered
            for keyword in ["多组学", "gwas", "基因", "单细胞", "rna", "测序", "组学", "omics"]
        )

    def _is_role_relevant(self, role: AgentRole, clinical_question: str) -> bool:
        lowered = (clinical_question or "").lower()
        role_keywords = {
            AgentRole.PHARMACOGENOMICS_EXPERT: ["药物基因组", "基因", "药物反应", "代谢"],
            AgentRole.GWAS_EXPERT: ["gwas", "位点", "snp", "遗传", "基因"],
            AgentRole.SINGLE_CELL_ANALYST: ["单细胞", "scrna", "rna", "细胞", "转录组", "测序"],
            AgentRole.GALAXY_BRIDGE: ["多组学", "workflow", "gwas", "基因", "单细胞", "rna", "组学"],
            AgentRole.UX_RESEARCHER: ["用户", "体验", "界面", "平台", "交互"],
            AgentRole.DATA_ENGINEER: ["数据工程", "数据清洗", "etl", "数据库", "管线", "workflow"],
            AgentRole.TREND_RESEARCHER: ["趋势", "投稿", "期刊", "发表", "竞争", "转化"],
        }
        if role not in role_keywords:
            return True
        return any(keyword in lowered for keyword in role_keywords[role])
    
    async def create_roundtable(self, title: str, clinical_question: str) -> RoundTable:
        """创建新的圆桌会"""
        roundtable = RoundTable(
            id=str(uuid.uuid4()),
            title=title,
            clinical_question=clinical_question,
            participants=list(AgentRole),
            status=RoundTableStatus.INIT
        )
        self.sessions[roundtable.id] = roundtable
        return roundtable
    
    async def start_discussion(self, session_id: str):
        """开始圆桌讨论"""
        roundtable = self.sessions.get(session_id)
        if not roundtable:
            raise ValueError(f"Session {session_id} not found")
        
        roundtable.status = RoundTableStatus.PROBLEM_PRESENTATION
        if not any(msg.from_role != "user" for msg in roundtable.messages):
            kickoff_message = A2AMessage(
                id=str(uuid.uuid4()),
                session_id=session_id,
                from_role=AgentRole.CLINICAL_DIRECTOR,
                to_role="all",
                type=MessageType.INTRODUCTION,
                content=self._build_kickoff_placeholder(roundtable),
                metadata={
                    "stage": "problem_presentation",
                    "round": 0,
                    "is_kickoff_placeholder": True,
                    "clinical_question": roundtable.clinical_question,
                    "title": roundtable.title,
                }
            )
            await self._broadcast_message(kickoff_message)
            roundtable.messages.append(kickoff_message)
        await self._run_initial_discussion_burst(session_id)

    async def _run_initial_discussion_burst(self, session_id: str):
        """首轮只给一个可执行开场，不自动把整套阶段一次跑完。"""
        roundtable = self.sessions[session_id]
        roundtable.current_round += 1

        stage = "problem_presentation"
        stage_config = DISCUSSION_STAGES.get(stage, {})
        stage_instruction = self._build_stage_instruction(stage_config, stage, roundtable.clinical_question)
        leader = AgentRole.CLINICAL_DIRECTOR
        leader_agent = self.agents[leader]

        init_message = A2AMessage(
            id="initial_burst",
            session_id=session_id,
            from_role=leader,
            to_role="all",
            type=MessageType.PROPOSAL,
            content=stage_instruction,
            metadata={
                "clinical_question": roundtable.clinical_question,
                "title": roundtable.title,
                "stage": stage,
            }
        )

        leader_response = await leader_agent.generate_response(
            init_message,
            roundtable.messages,
            stage,
            roundtable
        )

        leader_message = A2AMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            from_role=leader,
            to_role="all",
            type=MessageType.PROPOSAL,
            content=leader_response,
            metadata={
                "stage": stage,
                "round": roundtable.current_round,
                "clinical_question": roundtable.clinical_question,
                "title": roundtable.title,
            }
        )
        await self._broadcast_message(leader_message)
        roundtable.messages.append(leader_message)

        for role in [role for role in self._select_kickoff_roles(roundtable) if role != leader]:
            agent = self.agents[role]
            context_message = A2AMessage(
                id=f"kickoff_{role.value}",
                session_id=session_id,
                from_role=role,
                to_role="all",
                type=MessageType.FEEDBACK,
                content=f"""{stage_instruction}
请只补你负责的最关键一项交付物，不要重复他人已经说过的背景。""",
                metadata={
                    "clinical_question": roundtable.clinical_question,
                    "title": roundtable.title,
                    "stage": stage,
                }
            )

            response = await agent.generate_response(context_message, roundtable.messages, stage, roundtable)
            response_with_citations, citations = citation_manager.add_citations_to_content(
                response,
                role.value
            )

            if citations:
                citation_manager.citations.extend(citations)
                seen_ids = set()
                unique_citations = []
                for cite in citation_manager.citations:
                    if cite['id'] not in seen_ids:
                        seen_ids.add(cite['id'])
                        unique_citations.append(cite)
                citation_manager.citations = unique_citations

            message = A2AMessage(
                id=str(uuid.uuid4()),
                session_id=session_id,
                from_role=role,
                to_role="all",
                type=MessageType.FEEDBACK,
                content=response_with_citations,
                metadata={
                    "stage": stage,
                    "round": roundtable.current_round,
                    "clinical_question": roundtable.clinical_question,
                    "title": roundtable.title,
                    "citations": [c['id'] for c in citations]
                }
            )
            await self._broadcast_message(message)
            roundtable.messages.append(message)
            await asyncio.sleep(0.6)

    async def _safe_run_discussion_flow(self, session_id: str):
        """包装首轮自动讨论，避免后台任务异常被悄悄吞掉。"""
        try:
            await self._run_discussion_flow(session_id)
        except Exception as exc:
            print(f"Discussion flow failed for {session_id}: {exc}")
            traceback.print_exc()
    
    async def _run_discussion_flow(self, session_id: str):
        """运行讨论流程 - 支持用户随时插话"""
        roundtable = self.sessions[session_id]

        # 完整的9阶段讨论流程，包含全部14个Agent
        stages = [
            ("problem_presentation", AgentRole.CLINICAL_DIRECTOR),           # 阶段1: 临床问题陈述
            ("literature_review", AgentRole.PHD_STUDENT),                   # 阶段2: 文献调研
            ("study_design", AgentRole.EPIDEMIOLOGIST),                     # 阶段3: 研究方案设计
            ("bioinformatics_plan", AgentRole.GALAXY_BRIDGE),               # 阶段4: 生物信息学分析计划
            ("statistical_plan", AgentRole.STATISTICIAN),                   # 阶段5: 统计分析计划
            ("crf_design", AgentRole.STATISTICIAN),                         # 阶段6: 数据采集表设计
            ("execution_plan", AgentRole.RESEARCH_NURSE),                   # 阶段7: 执行计划制定
            ("quality_review", AgentRole.QA_EXPERT),                        # 阶段8: 质量审核
            ("consensus", AgentRole.CLINICAL_DIRECTOR),                     # 阶段9: 共识达成
        ]
        if not self._requires_bioinformatics_stage(roundtable.clinical_question):
            stages = [stage for stage in stages if stage[0] != "bioinformatics_plan"]

        for stage_name, leader_role in stages:
            # 检查是否有用户最近插话，如果有，先处理用户问题
            if self._has_recent_user_message(session_id, seconds=10):
                await asyncio.sleep(1)
                continue  # 跳过当前阶段，让用户主导

            await self._run_stage(session_id, stage_name, leader_role)

            # 阶段之间给用户更多阅读时间，并检查用户是否有输入
            for _ in range(3):
                await asyncio.sleep(0.8)
                if self._has_recent_user_message(session_id, seconds=2):
                    break  # 用户插话了，提前结束等待

        # 完成讨论
        if roundtable.status != RoundTableStatus.COMPLETED:
            # 临床主任总结
            await self._clinical_director_summary(session_id)

    async def _clinical_director_summary(self, session_id: str):
        """临床主任总结讨论内容"""
        roundtable = self.sessions.get(session_id)
        if not roundtable:
            return

        if any((message.metadata or {}).get("is_final_summary") for message in roundtable.messages):
            return
        
        roundtable.status = RoundTableStatus.COMPLETED
        roundtable.completed_at = datetime.utcnow()
        
        # 构建总结提示
        summary_prompt = f"""作为临床主任，请对本次圆桌讨论进行全面总结。

研究主题：{roundtable.title}
临床问题：{roundtable.clinical_question}

请综合各位专家的意见，给出以下总结：

1. **研究设计共识**：我们最终确定采用什么研究设计？为什么选择这个设计？

2. **关键决策点**：
   - 样本量：多少例？如何计算的？
   - 纳入/排除标准：核心标准是什么？
   - 干预措施：试验组和对照组分别是什么？
   - 主要终点：如何定义？
   - 统计方法：采用什么分析方法？

3. **专家建议汇总**：
   - 文献调研专家的关键发现
   - 流行病学家的设计建议
   - 统计学家的分析建议
   - 研究护士的执行建议

4. **下一步行动计划**：
   - 需要优先完成的事项
   - 潜在风险和应对措施
   - 建议的时间节点

5. **临床意义**：这项研究对临床实践可能产生什么影响？

请以专业、权威的语气撰写，体现临床主任的领导力和专业判断。"""

        # 创建总结请求消息
        summary_request = A2AMessage(
            id="summary_request",
            session_id=session_id,
            from_role="system",
            to_role="clinical_director",
            type=MessageType.SUMMARY,
            content=summary_prompt,
            metadata={
                "clinical_question": roundtable.clinical_question,
                "title": roundtable.title,
                "is_summary": True
            }
        )
        
        # 获取临床主任的总结
        clinical_director = self.agents[AgentRole.CLINICAL_DIRECTOR]
        summary_content = await clinical_director.generate_response(
            summary_request,
            roundtable.messages,
            "summary",
            roundtable
        )
        
        # 格式化总结内容
        formatted_summary = f"""📋 **讨论总结报告**

{summary_content}

---

💡 **提示**：讨论已完成！您可以随时发送消息继续探讨特定问题，或导出完整的研究方案。"""

        # 添加引用
        summary_with_citations, citations = citation_manager.add_citations_to_content(
            formatted_summary,
            "clinical_director"
        )
        
        if citations:
            citation_manager.citations.extend(citations)
            seen_ids = set()
            unique_citations = []
            for cite in citation_manager.citations:
                if cite['id'] not in seen_ids:
                    seen_ids.add(cite['id'])
                    unique_citations.append(cite)
            citation_manager.citations = unique_citations

        # 发送总结消息
        summary_msg = A2AMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            from_role=AgentRole.CLINICAL_DIRECTOR,
            to_role="all",
            type=MessageType.SUMMARY,
            content=summary_with_citations,
            metadata={
                "is_final_summary": True,
                "clinical_question": roundtable.clinical_question,
                "title": roundtable.title,
                "citations": [c['id'] for c in citations]
            }
        )
        
        await self._broadcast_message(summary_msg)
        roundtable.messages.append(summary_msg)
        
        print(f"✅ Session {session_id}: 临床主任总结完成")

    def _has_recent_user_message(self, session_id: str, seconds: int = 10) -> bool:
        """检查最近是否有用户消息"""
        roundtable = self.sessions.get(session_id)
        if not roundtable or not roundtable.messages:
            return False

        from datetime import timedelta
        recent_threshold = datetime.utcnow() - timedelta(seconds=seconds)

        for msg in reversed(roundtable.messages[-5:]):  # 只检查最近5条
            if msg.from_role == "user" and msg.created_at > recent_threshold:
                return True
        return False

    def _role_spoke_recently(self, session_id: str, role: AgentRole, seconds: int = 2) -> bool:
        """避免用户一催促就让同一位专家在几秒内重复发两次相似内容。"""
        roundtable = self.sessions.get(session_id)
        if not roundtable or not roundtable.messages:
            return False

        from datetime import timedelta
        recent_threshold = datetime.utcnow() - timedelta(seconds=seconds)

        for msg in reversed(roundtable.messages[-8:]):
            from_role = msg.from_role.value if hasattr(msg.from_role, "value") else str(msg.from_role)
            if from_role == role.value and msg.created_at > recent_threshold:
                return True
        return False
    
    async def _run_stage(self, session_id: str, stage: str, leader: AgentRole):
        """运行单个讨论阶段"""
        roundtable = self.sessions[session_id]
        roundtable.current_round += 1
        
        stage_config = DISCUSSION_STAGES.get(stage, {})
        prompt = stage_config.get("prompt", "请发表你的观点")
        participant_roles = [
            role for role in self._get_stage_roles(stage, roundtable)
            if role != leader
        ]

        stage_instruction = self._build_stage_instruction(stage_config, stage, roundtable.clinical_question)
        
        # 阶段引导者发言
        leader_agent = self.agents[leader]
        
        # 创建引导消息，包含研究基本信息
        init_message = A2AMessage(
            id="init",
            session_id=session_id,
            from_role=leader,
            to_role="all",
            type=MessageType.PROPOSAL,
            content=stage_instruction,
            metadata={
                "clinical_question": roundtable.clinical_question,
                "title": roundtable.title,
                "stage": stage
            }
        )
        
        leader_response = await leader_agent.generate_response(
            init_message,
            roundtable.messages,
            stage,
            roundtable
        )
        
        leader_message = A2AMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            from_role=leader,
            to_role="all",
            type=MessageType.PROPOSAL,
            content=leader_response,
            metadata={
                "stage": stage, 
                "round": roundtable.current_round,
                "clinical_question": roundtable.clinical_question,
                "title": roundtable.title
            }
        )
        await self._broadcast_message(leader_message)
        roundtable.messages.append(leader_message)

        if self._has_recent_user_message(session_id, seconds=2):
            return
        
        # 只让当前阶段最相关的 Agent 响应，避免 14 位 Agent 轮流说模板话
        for role in participant_roles:
            if self._has_recent_user_message(session_id, seconds=2):
                break
            agent = self.agents[role]
            
            # 创建包含研究信息的上下文消息
            context_message = A2AMessage(
                id="context",
                session_id=session_id,
                from_role=role,
                to_role="all",
                type=MessageType.FEEDBACK,
                content=f"""{stage_instruction}
请直接回应刚才的讨论，并补充你负责的可执行内容。优先给出数字、字段、流程、风险点或交付物。""",
                metadata={
                    "clinical_question": roundtable.clinical_question,
                    "title": roundtable.title,
                    "stage": stage
                }
            )
            
            response = await agent.generate_response(context_message, roundtable.messages, stage, roundtable)
            
            # 添加引用文献
            response_with_citations, citations = citation_manager.add_citations_to_content(
                response,
                role.value
            )
            
            # 保存引用
            if citations:
                citation_manager.citations.extend(citations)
                # 去重
                seen_ids = set()
                unique_citations = []
                for cite in citation_manager.citations:
                    if cite['id'] not in seen_ids:
                        seen_ids.add(cite['id'])
                        unique_citations.append(cite)
                citation_manager.citations = unique_citations
            
            message = A2AMessage(
                id=str(uuid.uuid4()),
                session_id=session_id,
                from_role=role,
                to_role="all",
                type=MessageType.FEEDBACK,
                content=response_with_citations,
                metadata={
                    "stage": stage, 
                    "round": roundtable.current_round,
                    "clinical_question": roundtable.clinical_question,
                    "title": roundtable.title,
                    "citations": [c['id'] for c in citations]
                }
            )
            await self._broadcast_message(message)
            roundtable.messages.append(message)
            await asyncio.sleep(0.8)
    
    async def _broadcast_message(self, message: A2AMessage):
        """广播消息给所有监听器"""
        for callback in list(self.message_callbacks):
            try:
                await callback(message)
            except Exception as e:
                print(f"Callback error: {e}")
    
    async def user_send_message(self, session_id: str, content: str, to_role: str = "all"):
        """用户发送消息 - 支持随时插话"""
        roundtable = self.sessions.get(session_id)
        if not roundtable:
            raise ValueError(f"Session {session_id} not found")

        message = A2AMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            from_role="user",
            to_role=to_role,
            type=MessageType.QUESTION,
            content=content
        )

        await self._broadcast_message(message)
        roundtable.messages.append(message)

        # 先立即返回用户消息，再由后台继续多 Agent 响应，避免前端请求超时
        asyncio.create_task(self._safe_handle_user_intervention(session_id, content, to_role))

    async def _safe_handle_user_intervention(self, session_id: str, user_content: str, to_role: str):
        """后台安全处理用户插话，避免异常中断主请求"""
        roundtable = self.sessions.get(session_id)
        if not roundtable:
            return
        try:
            await self._handle_user_intervention(session_id, user_content, to_role, roundtable)
        except Exception as exc:
            print(f"User intervention handling failed for {session_id}: {exc}")

    async def _handle_user_intervention(
        self,
        session_id: str,
        user_content: str,
        to_role: str,
        roundtable: RoundTable
    ):
        """处理用户插话 - 智能分配回应的Agent"""
        normalized = user_content.strip().lower()
        explicit_stage = self._infer_requested_stage(user_content)
        should_stage_drive = explicit_stage and any(
            marker in normalized for marker in ["阶段", "进入", "推进", "先做", "先把", "当前"]
        )

        if re.match(r"^(好的|继续|继续讨论|开始讨论|开始|收到|ok|okay|继续吧)([。！，,\s].*)?$", normalized) or should_stage_drive:
            target_stage = explicit_stage or self._get_next_stage(roundtable)
            follow_up_prompt = self._build_continue_prompt(roundtable, user_content, target_stage)
            responding_agents = self._select_continue_roles(roundtable, follow_up_prompt, target_stage)
            responded = False

            for role in responding_agents:
                if self._role_spoke_recently(session_id, role):
                    continue
                await self._agent_respond_to_user(
                    session_id,
                    role,
                    follow_up_prompt,
                    original_question=user_content,
                    stage=target_stage
                )
                responded = True
                await asyncio.sleep(0.8)

            if not responded and responding_agents:
                await self._agent_respond_to_user(
                    session_id,
                    responding_agents[0],
                    follow_up_prompt,
                    original_question=user_content,
                    stage=target_stage
                )

            if target_stage == "consensus" and roundtable.status != RoundTableStatus.COMPLETED:
                await asyncio.sleep(0.4)
                await self._clinical_director_summary(session_id)
            return

        if re.search(r"(总结|生成总结|最终总结|最终报告|生成报告|导出报告|形成报告)", normalized):
            await self._clinical_director_summary(session_id)
            return

        # 如果用户指定了特定Agent，直接由该Agent回应
        if to_role != "all" and to_role in [r.value for r in AgentRole]:
            await self._agent_respond_to_user(
                session_id,
                AgentRole(to_role),
                user_content,
                stage=self._get_latest_stage(roundtable)
            )
            return

        # 根据用户问题的关键词，选择最相关的 Agent 回应
        keywords = {
            AgentRole.CLINICAL_DIRECTOR: ["临床", "患者", "治疗", "诊断", "症状", "疗效", "安全性", "不良事件", "适应", "禁忌"],
            AgentRole.PHD_STUDENT: ["文献", "检索", "综述", "既往", "证据", "指南", "推荐", "文献综述", "研究现状"],
            AgentRole.EPIDEMIOLOGIST: ["设计", "方法", "偏倚", "样本", "队列", "对照", "随机", "盲法", "质量", "纳入", "排除"],
            AgentRole.STATISTICIAN: ["统计", "样本量", "效能", "分析", "检验", "P值", "置信区间", "多因素", "回归", "显著性", "终点", "字段", "变量", "crf", "表格", "sap"],
            AgentRole.RESEARCH_NURSE: ["执行", "操作", "随访", "数据", "CRF", "表格", "字段", "流程", "质控", "实施", "可行", "访视", "录入", "sop", "培训", "依从性"],
            AgentRole.PHARMACOGENOMICS_EXPERT: ["药物基因组", "基因", "用药", "代谢", "药敏", "不良反应"],
            AgentRole.GWAS_EXPERT: ["gwas", "位点", "snp", "遗传", "变异", "表型"],
            AgentRole.SINGLE_CELL_ANALYST: ["单细胞", "scrna", "细胞群", "转录组", "测序"],
            AgentRole.GALAXY_BRIDGE: ["组学", "workflow", "管线", "galaxy", "多组学"],
            AgentRole.UX_RESEARCHER: ["体验", "界面", "交互", "使用流程"],
            AgentRole.DATA_ENGINEER: ["数据工程", "清洗", "etl", "管道", "数据库", "整合"],
            AgentRole.TREND_RESEARCHER: ["趋势", "热点", "投稿", "期刊", "创新点", "竞争"],
            AgentRole.EXPERIMENT_TRACKER: ["里程碑", "进度", "追踪", "排期", "推进"],
            AgentRole.QA_EXPERT: ["qa", "质控", "核查", "一致性", "偏差", "复核"],
        }

        # 计算每个Agent的相关性得分
        scores = {}
        user_content_lower = user_content.lower()
        for role, words in keywords.items():
            score = sum(1 for word in words if word in user_content_lower)
            if score > 0:
                scores[role] = score

        # 对用户明确要求的交付物做加权，优先把问题分配给能给出具体产物的专家
        if any(word in user_content_lower for word in ["crf", "字段", "表格", "访视", "录入"]):
            scores[AgentRole.RESEARCH_NURSE] = scores.get(AgentRole.RESEARCH_NURSE, 0) + 3
            scores[AgentRole.STATISTICIAN] = scores.get(AgentRole.STATISTICIAN, 0) + 2
        if any(word in user_content_lower for word in ["样本量", "终点", "sap", "统计"]):
            scores[AgentRole.STATISTICIAN] = scores.get(AgentRole.STATISTICIAN, 0) + 3
        if "偏倚" in user_content_lower:
            scores[AgentRole.EPIDEMIOLOGIST] = scores.get(AgentRole.EPIDEMIOLOGIST, 0) + 2

        concrete_markers = [
            "crf", "字段", "表格", "访视", "录入", "样本量", "终点", "sap",
            "统计", "下一步", "交付物", "方案", "偏倚", "质控", "sop", "里程碑"
        ]

        # 如果没有匹配到关键词，用当前阶段的默认协作组合兜底，而不是只让临床主任应付一句
        if not scores:
            responding_agents = self._select_continue_roles(roundtable, user_content)
        else:
            # 选择得分最高的若干 Agent 回应；具体任务允许 3 位专家协作而不是 1-2 位模板式接话
            sorted_roles = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            max_responders = 4 if any(word in user_content_lower for word in concrete_markers) else 3
            responding_agents = [role for role, _ in sorted_roles[:max_responders]]

        if any(word in user_content_lower for word in ["crf", "字段", "表格", "访视", "录入", "sop"]) and AgentRole.RESEARCH_NURSE not in responding_agents:
            responding_agents.append(AgentRole.RESEARCH_NURSE)

        if any(word in user_content_lower for word in ["样本量", "终点", "sap", "统计"]) and AgentRole.STATISTICIAN not in responding_agents:
            responding_agents.insert(0, AgentRole.STATISTICIAN)

        if any(word in user_content_lower for word in ["偏倚", "纳入", "排除", "设计", "随机", "对照"]) and AgentRole.EPIDEMIOLOGIST not in responding_agents:
            responding_agents.append(AgentRole.EPIDEMIOLOGIST)

        # 去重并保持顺序
        deduped_agents = []
        for role in responding_agents:
            if role not in deduped_agents:
                deduped_agents.append(role)
        responding_agents = deduped_agents[:4]

        # 让这些Agent依次回应
        for role in responding_agents:
            if self._role_spoke_recently(session_id, role):
                continue
            await self._agent_respond_to_user(
                session_id,
                role,
                user_content,
                stage=self._get_latest_stage(roundtable)
            )
            await asyncio.sleep(0.8)

    async def _agent_respond_to_user(
        self,
        session_id: str,
        role: AgentRole,
        user_content: str,
        original_question: Optional[str] = None,
        stage: Optional[str] = None
    ):
        """单个Agent回应用户"""
        roundtable = self.sessions.get(session_id)
        agent = self.agents[role]

        # 构建一个临时的消息对象，包含研究基本信息
        user_message = A2AMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            from_role="user",
            to_role=role.value,
            type=MessageType.QUESTION,
            content=user_content,
            metadata={
                "clinical_question": roundtable.clinical_question,
                "title": roundtable.title
            }
        )

        # 生成回应
        response = await agent.generate_response(
            user_message,
            roundtable.messages,
            stage or "user_intervention",
            roundtable
        )
        
        # 添加引用文献
        response_with_citations, citations = citation_manager.add_citations_to_content(
            response, 
            role.value
        )
        
        # 保存引用
        if citations:
            citation_manager.citations.extend(citations)
            # 去重
            seen_ids = set()
            unique_citations = []
            for cite in citation_manager.citations:
                if cite['id'] not in seen_ids:
                    seen_ids.add(cite['id'])
                    unique_citations.append(cite)
            citation_manager.citations = unique_citations

        response_msg = A2AMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            from_role=role,
            to_role="user",
            type=MessageType.FEEDBACK,
            content=response_with_citations,
            metadata={
                "responding_to_user": True, 
                "original_question": original_question or user_content,
                "stage": stage or self._get_latest_stage(roundtable),
                "clinical_question": roundtable.clinical_question,
                "title": roundtable.title,
                "citations": [c['id'] for c in citations]
            }
        )

        await self._broadcast_message(response_msg)
        roundtable.messages.append(response_msg)
    
    def get_session(self, session_id: str) -> Optional[RoundTable]:
        """获取会话"""
        return self.sessions.get(session_id)
    
    def get_agent_info(self) -> List[Dict]:
        """获取所有Agent信息"""
        return [
            {
                "role": role.value,
                "name": agent.name,
                "avatar": agent.avatar,
                "expertise": agent.expertise
            }
            for role, agent in self.agents.items()
        ]


# 全局协调器实例
orchestrator = A2AOrchestrator()
