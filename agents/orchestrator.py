import asyncio
import uuid
from typing import List, Dict, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
import json

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
        
        prompt += f"""
=== 当前消息 ===
来自: {message.from_role.value if hasattr(message.from_role, 'value') else str(message.from_role)}
内容: {message.content}

=== 你的任务 ===
请根据你的专业角色、研究的基本信息（研究标题和临床问题）以及讨论上下文，给出专业、详细的回应。
要求:
1. 使用中文回答，内容必须紧扣上述"临床问题"
2. 体现你的专业视角，给出具体可行的建议
3. 如果提到疾病名称、干预措施或终点指标，请使用临床问题中提到的具体内容
4. 如果有不同意见，请礼貌提出；如果同意，请补充你的专业建议

请给出你的回应:"""
        
        return prompt
    
    def _fallback_response(self, message, context, stage):
        """备用响应（当 LLM 失败时使用）"""
        responses = {
            AgentRole.CLINICAL_DIRECTOR: "从临床角度来看，这个研究方向很有价值。我建议我们进一步讨论具体的实施方案。",
            AgentRole.PHD_STUDENT: "我会记录这个要点，并查找相关文献支持。",
            AgentRole.EPIDEMIOLOGIST: "从方法学角度，我建议考虑选择偏倚的控制和样本量计算。",
            AgentRole.STATISTICIAN: "从统计学角度，我们需要明确主要终点和统计方法。",
            AgentRole.RESEARCH_NURSE: "从执行角度，我们需要考虑实际操作的可行性和质量控制。"
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
        self.message_callbacks.append(callback)
    
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
        
        # 自动触发第一轮讨论
        asyncio.create_task(self._run_discussion_flow(session_id))
    
    async def _run_discussion_flow(self, session_id: str):
        """运行讨论流程 - 支持用户随时插话"""
        roundtable = self.sessions[session_id]

        stages = [
            ("problem_presentation", AgentRole.CLINICAL_DIRECTOR),
            ("literature_review", AgentRole.PHD_STUDENT),
            ("study_design", AgentRole.EPIDEMIOLOGIST),
            ("statistical_plan", AgentRole.STATISTICIAN),
            ("execution_plan", AgentRole.RESEARCH_NURSE),
            ("consensus", AgentRole.CLINICAL_DIRECTOR),
        ]

        for stage_name, leader_role in stages:
            # 检查是否有用户最近插话，如果有，先处理用户问题
            if self._has_recent_user_message(session_id, seconds=10):
                await asyncio.sleep(3)  # 给用户时间阅读回应
                continue  # 跳过当前阶段，让用户主导

            await self._run_stage(session_id, stage_name, leader_role)

            # 阶段之间给用户更多阅读时间，并检查用户是否有输入
            for _ in range(6):  # 6秒等待时间，可被打断
                await asyncio.sleep(1)
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
    
    async def _run_stage(self, session_id: str, stage: str, leader: AgentRole):
        """运行单个讨论阶段"""
        roundtable = self.sessions[session_id]
        roundtable.current_round += 1
        
        stage_config = DISCUSSION_STAGES.get(stage, {})
        prompt = stage_config.get("prompt", "请发表你的观点")
        
        # 阶段引导者发言
        leader_agent = self.agents[leader]
        
        # 创建引导消息，包含研究基本信息
        init_message = A2AMessage(
            id="init",
            session_id=session_id,
            from_role=leader,
            to_role="all",
            type=MessageType.PROPOSAL,
            content=prompt,
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
        
        # 其他Agent依次响应
        for role in [r for r in AgentRole if r != leader]:
            agent = self.agents[role]
            
            # 创建包含研究信息的上下文消息
            context_message = A2AMessage(
                id="context",
                session_id=session_id,
                from_role=role,
                to_role="all",
                type=MessageType.FEEDBACK,
                content="请发表您的专业意见",
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
            await asyncio.sleep(1.5)  # 给用户阅读时间
    
    async def _broadcast_message(self, message: A2AMessage):
        """广播消息给所有监听器"""
        for callback in self.message_callbacks:
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

        # 分析用户问题，决定哪些Agent应该回应
        await self._handle_user_intervention(session_id, content, to_role)

    async def _handle_user_intervention(self, session_id: str, user_content: str, to_role: str):
        """处理用户插话 - 智能分配回应的Agent"""
        roundtable = self.sessions.get(session_id)

        # 如果用户指定了特定Agent，直接由该Agent回应
        if to_role != "all" and to_role in [r.value for r in AgentRole]:
            await self._agent_respond_to_user(session_id, AgentRole(to_role), user_content)
            return

        # 根据用户问题的关键词，选择最相关的1-2个Agent回应
        keywords = {
            AgentRole.CLINICAL_DIRECTOR: ["临床", "患者", "治疗", "诊断", "症状", "疗效", "安全性", "不良事件", "适应", "禁忌"],
            AgentRole.PHD_STUDENT: ["文献", "检索", "综述", "既往", "证据", "指南", "推荐", "文献综述", "研究现状"],
            AgentRole.EPIDEMIOLOGIST: ["设计", "方法", "偏倚", "样本", "队列", "对照", "随机", "盲法", "质量"],
            AgentRole.STATISTICIAN: ["统计", "样本量", "效能", "分析", "检验", "P值", "置信区间", "多因素", "回归", "显著性"],
            AgentRole.RESEARCH_NURSE: ["执行", "操作", "随访", "数据", "CRF", "表格", "流程", "质控", "实施", "可行"]
        }

        # 计算每个Agent的相关性得分
        scores = {}
        user_content_lower = user_content.lower()
        for role, words in keywords.items():
            score = sum(1 for word in words if word in user_content_lower)
            if score > 0:
                scores[role] = score

        # 如果没有匹配到关键词，选择临床主任作为默认回应者
        if not scores:
            scores = {AgentRole.CLINICAL_DIRECTOR: 1}

        # 选择得分最高的1-2个Agent回应（给用户阅读时间，不要太多Agent同时回应）
        sorted_roles = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        responding_agents = [role for role, _ in sorted_roles[:2]]

        # 让这些Agent依次回应
        for role in responding_agents:
            await self._agent_respond_to_user(session_id, role, user_content)
            await asyncio.sleep(1.5)  # 给用户阅读时间

    async def _agent_respond_to_user(self, session_id: str, role: AgentRole, user_content: str):
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
            "user_intervention",
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

        # 添加前缀，表明这是对用户问题的回应
        response_with_context = f"针对您的问题，{agent.name}回应道：\n\n{response_with_citations}"

        response_msg = A2AMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            from_role=role,
            to_role="user",
            type=MessageType.FEEDBACK,
            content=response_with_context,
            metadata={
                "responding_to_user": True, 
                "original_question": user_content,
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
