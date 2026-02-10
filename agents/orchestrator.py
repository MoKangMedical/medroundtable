import asyncio
import uuid
from typing import List, Dict, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
import json

from backend.models import A2AMessage, AgentRole, MessageType, RoundTable, RoundTableStatus
from agents.prompts import AGENT_PROFILES, DISCUSSION_STAGES


@dataclass
class Agent:
    role: AgentRole
    name: str
    avatar: str
    system_prompt: str
    expertise: List[str]
    llm_client: Optional[any] = None
    
    async def generate_response(
        self, 
        message: A2AMessage, 
        context: List[A2AMessage],
        stage: str
    ) -> str:
        responses = {
            AgentRole.CLINICAL_DIRECTOR: self._clinical_director_response,
            AgentRole.PHD_STUDENT: self._phd_student_response,
            AgentRole.EPIDEMIOLOGIST: self._epidemiologist_response,
            AgentRole.STATISTICIAN: self._statistician_response,
            AgentRole.RESEARCH_NURSE: self._research_nurse_response,
        }
        
        response_fn = responses.get(self.role, self._default_response)
        return await response_fn(message, context, stage)
    
    async def _clinical_director_response(self, message, context, stage):
        if stage == "problem_presentation":
            return """感谢大家参加今天的临床科研圆桌会。

我提出一个临床问题：我们科室最近在临床中发现，使用新型降糖药的2型糖尿病患者中，有一部分患者出现了意想不到的心血管获益。这个现象值得我们深入研究。

初步假设：这种新型降糖药可能通过某种机制对心血管系统产生保护作用。

从临床价值来看，如果得到证实，这将为2型糖尿病患者的心血管保护提供新的治疗选择。"""
        elif stage == "consensus":
            return "我同意这个方案。研究设计科学合理，既有创新性又有可行性。建议按计划执行。"
        else:
            return f"从临床角度来看，我认为{message.content[:50]}...这个方向是正确的。我们需要确保研究结果能够指导临床实践。"
    
    async def _phd_student_response(self, message, context, stage):
        if stage == "literature_review":
            return """我已经完成了文献检索。目前有以下发现：

1. 近5年有12项相关研究，主要集中在GLP-1受体激动剂和SGLT2抑制剂
2. EMPA-REG研究证实SGLT2抑制剂可降低心血管事件风险
3. 但关于这种新型药物的心血管获益机制，目前研究较少
4. 我们的研究将填补这一空白

建议参考的关键文献：
- Zinman et al. NEJM 2015 (EMPA-REG)
- Marso et al. NEJM 2016 (LEADER)"""
        else:
            return f"我记录了这个要点。关于{message.content[:50]}...我会整理到研究方案中。请问还有其他需要我补充的文献吗？"
    
    async def _epidemiologist_response(self, message, context, stage):
        if stage == "study_design":
            return """基于临床主任提出的问题和博士生的文献调研，我建议采用前瞻性队列研究设计：

**研究设计要点：**

1. **研究类型**: 多中心、前瞻性、队列研究
2. **纳入标准**: 
   - 18-75岁2型糖尿病患者
   - 糖化血红蛋白 7.0-10.0%
   - 无严重心血管疾病史

3. **排除标准**:
   - 严重肝肾功能不全
   - 既往心肌梗死史
   - 对研究药物过敏

4. **样本量**: 根据统计专家建议计算
5. **偏倚控制**: 采用倾向性评分匹配控制混杂

这个设计能够较好地回答研究问题，同时保证科学严谨性。"""
        else:
            return f"从方法学角度，{message.content[:50]}...这个设计需要注意选择偏倚的控制。建议增加一个外部验证队列。"
    
    async def _statistician_response(self, message, context, stage):
        if stage == "statistical_plan":
            return """**统计分析计划：**

1. **样本量计算**:
   - 假设HR=0.75，alpha=0.05，Power=80%
   - 考虑20%失访率
   - **需要样本：每组400例，共800例**

2. **主要分析**:
   - Cox比例风险模型比较两组心血管事件发生率
   - Kaplan-Meier曲线展示生存差异
   - Log-rank检验比较曲线差异

3. **次要分析**:
   - 多因素Cox回归调整混杂因素
   - 亚组分析（年龄、性别、基线HbA1c）
   - 敏感性分析

4. **图表生成**:
   - 基线特征表
   - 生存曲线图
   - 森林图展示亚组分析结果
   - 不良反应发生率图

5. **统计软件**: R 4.3.0 或 SAS 9.4"""
        elif stage == "crf_design":
            return """我已设计数据采集表格：

**CRF主要模块：**
1. 人口学信息（年龄、性别、BMI等）
2. 病史资料（糖尿病病程、并发症等）
3. 实验室检查（HbA1c、血脂、肾功能等）
4. 心血管终点事件（主要/次要终点）
5. 安全性数据（不良反应）

**数据验证规则：**
- 逻辑检查（如男患者排除妊娠）
- 范围检查（HbA1c 4-15%）
- 完整性检查（关键字段必填）"""
        else:
            return f"从统计学角度，{message.content[:50]}...建议采用分层分析控制混杂因素。P值<0.05认为有统计学意义。"
    
    async def _research_nurse_response(self, message, context, stage):
        if stage == "execution_plan":
            return """**执行计划：**

1. **人员分工**:
   - 研究医生：患者筛选、知情同意、医疗决策
   - 研究护士：数据录入、样本采集、随访
   - 数据管理员：数据核查、质量控制

2. **研究流程**:
   - Day -7: 筛选期，签署知情同意
   - Day 0: 基线访视，随机分组
   - Month 1, 3, 6: 随访访视
   - Month 12: 主要终点评估

3. **质量控制**:
   - 双人录入+逻辑核查
   - 10%源数据核查
   - 每月质量报告

4. **操作手册**: 
   我将制定详细的SOP，包括知情同意流程、数据录入规范、样本处理流程等。

5. **风险预案**:
   - 患者失访：多渠道联系，保留交通补贴
   - 数据缺失：及时追踪，质控提醒
   - 方案违背：记录报告，纠正预防措施"""
        else:
            return f"从执行角度，{message.content[:50]}...在临床操作中，我们需要特别注意知情同意的规范性。建议增加操作培训环节。"
    
    async def _default_response(self, message, context, stage):
        return f"收到。我同意上述观点，并会从我的专业角度提供支持。"


class A2AOrchestrator:
    def __init__(self):
        self.agents: Dict[AgentRole, Agent] = {}
        self.sessions: Dict[str, RoundTable] = {}
        self.message_callbacks: List[Callable] = []
        self._init_agents()
    
    def _init_agents(self):
        for role, profile in AGENT_PROFILES.items():
            self.agents[AgentRole(role)] = Agent(
                role=AgentRole(role),
                name=profile["name"],
                avatar=profile["avatar"],
                system_prompt=profile["system_prompt"],
                expertise=profile["expertise"]
            )
    
    def register_message_callback(self, callback: Callable):
        self.message_callbacks.append(callback)
    
    async def create_roundtable(self, title: str, clinical_question: str) -> RoundTable:
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
        roundtable = self.sessions.get(session_id)
        if not roundtable:
            raise ValueError(f"Session {session_id} not found")
        
        roundtable.status = RoundTableStatus.PROBLEM_PRESENTATION
        asyncio.create_task(self._run_discussion_flow(session_id))
    
    async def _run_discussion_flow(self, session_id: str):
        roundtable = self.sessions[session_id]
        
        stages = [
            ("problem_presentation", AgentRole.CLINICAL_DIRECTOR),
            ("literature_review", AgentRole.PHD_STUDENT),
            ("study_design", AgentRole.EPIDEMIOLOGIST),
            ("statistical_plan", AgentRole.STATISTICIAN),
            ("crf_design", AgentRole.STATISTICIAN),
            ("execution_plan", AgentRole.RESEARCH_NURSE),
            ("consensus", AgentRole.CLINICAL_DIRECTOR),
        ]
        
        for stage_name, leader_role in stages:
            await self._run_stage(session_id, stage_name, leader_role)
            await asyncio.sleep(1)
        
        roundtable.status = RoundTableStatus.COMPLETED
        roundtable.completed_at = datetime.utcnow()
    
    async def _run_stage(self, session_id: str, stage: str, leader: AgentRole):
        roundtable = self.sessions[session_id]
        roundtable.current_round += 1
        
        stage_config = DISCUSSION_STAGES.get(stage, {})
        prompt = stage_config.get("prompt", "请发表你的观点")
        
        leader_agent = self.agents[leader]
        leader_message = A2AMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            from_role=leader,
            to_role="all",
            type=MessageType.PROPOSAL,
            content=await leader_agent.generate_response(
                A2AMessage(
                    id="init",
                    session_id=session_id,
                    from_role=leader,
                    to_role="all",
                    type=MessageType.PROPOSAL,
                    content=prompt
                ),
                roundtable.messages,
                stage
            ),
            metadata={"stage": stage, "round": roundtable.current_round}
        )
        await self._broadcast_message(leader_message)
        roundtable.messages.append(leader_message)
        
        for role in [r for r in AgentRole if r != leader]:
            agent = self.agents[role]
            response = await agent.generate_response(leader_message, roundtable.messages, stage)
            
            message = A2AMessage(
                id=str(uuid.uuid4()),
                session_id=session_id,
                from_role=role,
                to_role="all",
                type=MessageType.FEEDBACK,
                content=response,
                metadata={"stage": stage, "round": roundtable.current_round}
            )
            await self._broadcast_message(message)
            roundtable.messages.append(message)
            await asyncio.sleep(0.5)
    
    async def _broadcast_message(self, message: A2AMessage):
        for callback in self.message_callbacks:
            try:
                await callback(message)
            except Exception as e:
                print(f"Callback error: {e}")
    
    async def user_send_message(self, session_id: str, content: str, to_role: str = "all"):
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
        
        if to_role != "all" and to_role in [r.value for r in AgentRole]:
            agent = self.agents[AgentRole(to_role)]
            response = await agent.generate_response(message, roundtable.messages, "general")
            
            response_msg = A2AMessage(
                id=str(uuid.uuid4()),
                session_id=session_id,
                from_role=AgentRole(to_role),
                to_role="user",
                type=MessageType.FEEDBACK,
                content=response
            )
            await self._broadcast_message(response_msg)
            roundtable.messages.append(response_msg)
    
    def get_session(self, session_id: str) -> Optional[RoundTable]:
        return self.sessions.get(session_id)
    
    def get_agent_info(self) -> List[Dict]:
        return [
            {
                "role": role.value,
                "name": agent.name,
                "avatar": agent.avatar,
                "expertise": agent.expertise
            }
            for role, agent in self.agents.items()
        ]


orchestrator = A2AOrchestrator()
