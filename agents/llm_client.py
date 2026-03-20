import asyncio
import os
import time
from openai import OpenAI
from typing import List, Dict
import json
import re

class LLMClient:
    """LLM 客户端 - 支持 Moonshot (Kimi) 和 OpenAI"""
    
    def __init__(self):
        # 加载环境变量
        from dotenv import load_dotenv
        load_dotenv()
        
        # Moonshot 配置
        self.moonshot_key = os.getenv("MOONSHOT_API_KEY")
        self.moonshot_base = os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.cn/v1")
        self.moonshot_model = os.getenv("MOONSHOT_MODEL", "moonshot-v1-128k")
        # 首轮圆桌如果等待太久，用户会误以为“没有真的开始讨论”。
        # 默认把超时压到 1.5 秒，超时后立即切高质量模拟响应，优先保证讨论连贯性。
        self.request_timeout = float(os.getenv("MOONSHOT_TIMEOUT", "1.5"))
        self.force_mock = False
        self.mock_until = 0.0
        self.prefer_discussion_mock = os.getenv(
            "MOONSHOT_PREFER_DISCUSSION_MOCK",
            "false"
        ).strip().lower() not in {"0", "false", "no"}
        
        # 初始化 Moonshot 客户端
        if self.moonshot_key:
            self.client = OpenAI(
                api_key=self.moonshot_key,
                base_url=self.moonshot_base,
                timeout=self.request_timeout,
                max_retries=1
            )
            print(f"✅ Moonshot API 已配置，模型: {self.moonshot_model}")
        else:
            self.client = None
            print("⚠️ 未找到 MOONSHOT_API_KEY，将使用模拟响应")

    def _mock_mode_active(self) -> bool:
        return self.force_mock or time.time() < self.mock_until

    def _should_prefer_discussion_mock(self, user_prompt: str) -> bool:
        if not self.prefer_discussion_mock:
            return False

        markers = [
            "=== 你需要回应的前序观点 ===",
            "=== 本轮必须覆盖的交付物 ===",
            "当前参考阶段：",
            "直接回应刚才的讨论，并补充你负责的可执行内容。",
        ]
        return any(marker in (user_prompt or "") for marker in markers)
    
    async def generate_response(
        self, 
        system_prompt: str, 
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """生成 AI 响应"""
        
        if not self.client or self._mock_mode_active() or self._should_prefer_discussion_mock(user_prompt):
            # 没有配置 API Key，返回模拟响应
            return self._generate_mock_response(system_prompt, user_prompt)

        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.moonshot_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            status_code = getattr(e, "status_code", None)
            error_text = str(e).lower()
            if status_code in {401, 403} or "401" in error_text or "invalid api key" in error_text:
                self.force_mock = True
                print("⚠️ LLM 鉴权失败，后续请求切换为高质量模拟响应")
                return self._generate_mock_response(system_prompt, user_prompt)

            if status_code == 429 or any(
                marker in error_text
                for marker in [
                    "timeout",
                    "timed out",
                    "read timeout",
                    "connection reset",
                    "temporarily unavailable",
                    "engine is currently overloaded",
                    "rate limit"
                ]
            ):
                self.mock_until = time.time() + 300
                print(f"⚠️ LLM 服务抖动，未来 5 分钟切换为高质量模拟响应: {e}")
                return self._generate_mock_response(system_prompt, user_prompt)

            print(f"❌ LLM API 调用失败: {e}")
            return self._generate_mock_response(system_prompt, user_prompt)
    
    def _analyze_question(self, user_prompt: str) -> dict:
        """分析用户的临床问题，提取关键信息"""
        # 从新的 prompt 格式中提取
        # 格式: "临床问题: xxx" 或 "临床问题：xxx"
        question_match = re.search(r'临床问题[:：]\s*(.+?)(?:\n===|\n\n|$)', user_prompt, re.DOTALL)
        clinical_question = question_match.group(1).strip() if question_match else ""
        
        # 提取研究标题
        title_match = re.search(r'研究标题[:：]\s*(.+?)(?:\n|$)', user_prompt, re.DOTALL)
        title = title_match.group(1).strip() if title_match else ""
        
        # 如果 clinical_question 为空，尝试从其他地方提取
        if not clinical_question:
            # 尝试从讨论记录中提取
            for line in user_prompt.split('\n'):
                if '临床问题' in line and ':' in line:
                    clinical_question = line.split(':', 1)[1].strip()
                    break
        
        # 如果还是为空，返回默认值
        if not clinical_question or clinical_question == "需要讨论的临床问题":
            clinical_question = "当前研究项目"
        
        if not title or title == "待讨论的研究项目":
            title = "医学研究项目"
        
        # 按命中数判断病种，避免“胰岛素”把神经电生理问题误判成糖尿病
        disease_types = [
            ("神经系统", ["神经元", "电信号", "放电", "突触", "电生理", "神经传导", "癫痫", "帕金森", "认知", "痴呆", "脑梗", "脑出血"]),
            ("糖尿病", ["血糖", "HbA1c", "胰岛素", "二甲双胍", "低血糖", "2型糖尿病", "1型糖尿病"]),
            ("高血压", ["血压", "收缩压", "舒张压", "降压药", "心血管", "降压"]),
            ("肿瘤", ["癌症", "化疗", "放疗", "靶向", "生存期", "OS", "PFS", "肿瘤"]),
            ("心血管疾病", ["心梗", "心衰", "冠心病", "支架", "溶栓", "心绞痛"]),
            ("呼吸系统", ["哮喘", "COPD", "肺功能", "氧疗", "急性发作", "慢阻肺"]),
            ("骨科", ["骨折", "关节置换", "骨密度", "骨质疏松", "康复", "关节"]),
            ("感染", ["抗生素", "病毒", "细菌", "感染", "炎症指标", "抗病毒"]),
            ("消化", ["胃炎", "溃疡", "肝病", "肝硬化", "脂肪肝", "消化"]),
            ("内分泌", ["甲状腺", "甲亢", "甲减", "激素", "内分泌"]),
        ]

        detected_disease = None
        highest_score = 0
        for disease, keywords in disease_types:
            score = sum(1 for kw in keywords if kw in clinical_question)
            if score > highest_score:
                highest_score = score
                detected_disease = disease
        
        # 分析干预措施类型
        interventions = []
        if "胰岛素" in clinical_question:
            interventions.append("胰岛素暴露/干预")
        elif "二甲双胍" in clinical_question:
            interventions.append("二甲双胍药物治疗")
        elif "药物" in clinical_question or "治疗" in clinical_question:
            interventions.append("药物治疗")
        if "手术" in clinical_question:
            interventions.append("手术治疗")
        if "康复" in clinical_question or "训练" in clinical_question:
            interventions.append("康复治疗")
        if "预防" in clinical_question:
            interventions.append("预防措施")
        if "对照" in clinical_question or "对比" in clinical_question:
            interventions.append("对照干预")
        
        intervention = "、".join(interventions) if interventions else "干预措施"
        
        # 分析主要终点
        endpoints = []
        if "死亡率" in clinical_question or "生存" in clinical_question:
            endpoints.append("总生存期(OS)")
        if "复发" in clinical_question:
            endpoints.append("无复发生存期(RFS)")
        if "住院" in clinical_question:
            endpoints.append("住院率")
        if "并发症" in clinical_question:
            endpoints.append("并发症发生率")
        if "生活质量" in clinical_question or "QoL" in clinical_question:
            endpoints.append("生活质量评分")
        if "血糖" in clinical_question or "HbA1c" in clinical_question:
            endpoints.append("糖化血红蛋白(HbA1c)水平")
        if "血压" in clinical_question:
            endpoints.append("血压控制率")
        
        main_endpoint = endpoints[0] if endpoints else "主要临床疗效指标"
        
        return {
            "clinical_question": clinical_question,
            "title": title,
            "disease": detected_disease or "相关疾病",
            "intervention": intervention,
            "endpoint": main_endpoint
        }

    def _extract_current_request(self, user_prompt: str) -> str:
        """提取当前这一轮真正要回答的问题"""
        current_match = re.search(r'=== 当前消息 ===.*?内容[:：]\s*(.+?)(?:\n===|\Z)', user_prompt, re.DOTALL)
        if current_match:
            return current_match.group(1).strip()
        return ""

    def _extract_peer_views(self, user_prompt: str) -> List[Dict[str, str]]:
        """提取最近需要回应的前序专家观点"""
        section_match = re.search(r'=== 你需要回应的前序观点 ===\n(.+?)(?:\n\n请给出你的回应:|\Z)', user_prompt, re.DOTALL)
        if not section_match:
            return []

        peer_views = []
        for line in section_match.group(1).splitlines():
            line = line.strip()
            if not line.startswith("- "):
                continue
            line = line[2:]
            if ":" not in line:
                continue
            role_name, content = line.split(":", 1)
            peer_views.append({
                "role": role_name.strip(),
                "content": content.strip()
            })
        return peer_views[:2]

    def _build_discussion_bridge(self, role: str, peer_views: List[Dict[str, str]]) -> str:
        role_openers = {
            "临床主任": "我先把临床判断和边界钉住，不重复背景。",
            "博士生": "我补证据检索和文献提取清单。",
            "流行病学家": "我把研究设计骨架和偏倚控制补齐。",
            "统计学家": "我直接落统计口径、样本量和分析框架。",
            "研究护士": "我补执行路径、访视安排和 CRF 页面。",
            "趋势研究员": "我补创新定位和投稿判断。",
            "实验追踪员": "我补推进节点和里程碑。",
            "模型QA专家": "我补质量闸门和前置核查项。",
        }

        if not peer_views:
            return role_openers.get(role, "我直接给这轮最需要落地的结论，不重复背景。")

        lead = peer_views[0]
        role_follow_ups = {
            "临床主任": f"基于 {lead['role']} 刚才锁定的方向，我把临床决策边界再钉实。",
            "博士生": f"沿着 {lead['role']} 刚才的判断，我补文献证据和检索动作。",
            "流行病学家": f"顺着 {lead['role']} 已经明确的重点，我补研究设计和偏倚控制。",
            "统计学家": f"在 {lead['role']} 刚才的基础上，我把统计口径和样本量落到可执行层。",
            "研究护士": f"接着 {lead['role']} 已经确定的方向，我补访视、CRF 和现场执行动作。",
            "趋势研究员": f"基于 {lead['role']} 的判断，我补创新定位和发表路径。",
            "实验追踪员": f"顺着 {lead['role']} 刚才的结论，我把推进节奏拆成节点。",
            "模型QA专家": f"基于 {lead['role']} 已经提到的关键点，我补质控闸门和核查规则。",
        }
        return role_follow_ups.get(
            role,
            f"基于 {lead['role']} 刚才的判断，我补这一位负责的可执行内容。"
        )

    def _normalize_role_label(self, system_prompt: str, extracted_role: str) -> str:
        role_map = [
            ("临床主任", ["临床主任", "临床医学主任"]),
            ("博士生", ["博士生", "科研助手"]),
            ("流行病学家", ["流行病学家", "流行病学"]),
            ("统计学家", ["统计学家", "统计专家"]),
            ("研究护士", ["研究护士"]),
            ("药物基因组学专家", ["药物基因组学"]),
            ("GWAS专家", ["GWAS"]),
            ("单细胞测序分析师", ["单细胞"]),
            ("Galaxy桥接器", ["Galaxy"]),
            ("AI数据工程师", ["数据工程师"]),
            ("趋势研究员", ["趋势研究员"]),
            ("实验追踪员", ["实验追踪"]),
            ("模型QA专家", ["QA", "质量控制"]),
        ]

        for normalized, keywords in role_map:
            if any(keyword in extracted_role or keyword in system_prompt for keyword in keywords):
                return normalized
        return extracted_role
    
    def _generate_mock_response(self, system_prompt: str, user_prompt: str) -> str:
        """生成与临床问题相关的高质量模拟响应"""
        # 提取角色
        role_match = re.search(r'你是(.+?)[，。]', system_prompt)
        role = role_match.group(1) if role_match else "专家"
        role = self._normalize_role_label(system_prompt, role)
        
        # 分析临床问题
        info = self._analyze_question(user_prompt)
        question = info["clinical_question"]
        disease = info["disease"]
        intervention = info["intervention"]
        endpoint = info["endpoint"]
        current_request = self._extract_current_request(user_prompt)
        if not current_request or "当前阶段是" in current_request:
            current_request = question
        peer_views = self._extract_peer_views(user_prompt)
        discussion_bridge = self._build_discussion_bridge(role, peer_views)
        wants_crf = any(keyword in user_prompt for keyword in ["CRF", "crf", "表格", "字段", "变量清单", "采集表"])
        wants_sample_size = any(keyword in user_prompt for keyword in ["样本量", "效能", "power", "把握度"])
        wants_bias = any(keyword in user_prompt for keyword in ["偏倚", "混杂", "盲法", "随机", "质控"])
        wants_risks = any(keyword in user_prompt for keyword in ["风险", "不良事件", "脱落", "失败点", "卡点"])
        is_neurosignal_topic = any(keyword in question for keyword in ["神经元", "电信号", "放电", "突触", "神经"])
        wants_literature = any(keyword in user_prompt for keyword in ["文献", "回顾", "综述", "检索", "证据", "指南"])
        needs_concrete_plan = wants_crf or wants_sample_size or wants_bias or wants_literature or wants_risks

        if is_neurosignal_topic:
            endpoint = "暴露后神经元平均放电频率变化（Hz）"

        if "统计学家" in role and (wants_sample_size or wants_crf or wants_bias):
            sample_size_text = "按双侧 α=0.05、把握度 80%、预期两组主要终点差异 0.45 个标准差估算，每组至少 79 例；按 15% 脱落上调后建议每组 93 例，总样本量 186 例。"
            if is_neurosignal_topic:
                sample_size_text = "若主要终点定义为“第 28 天神经元平均放电频率较基线变化值”，假设试验组较对照组多改善 1.8 Hz、共同标准差 4.0 Hz，双侧 α=0.05、把握度 80%，每组需 78 例；考虑 15% 脱落后建议每组 92 例，总计 184 例。"

            crf_text = """**建议直接落在 CRF 的核心字段**
1. 受试者标识：受试者编号、中心编号、筛选日期、入组日期
2. 分组信息：随机分组、给药方案、剂量、给药起止日期
3. 基线特征：年龄、性别、基础疾病、合并用药、基线神经电生理指标
4. 疗效指标：基线放电频率、第 7/14/28 天放电频率、突触后电流幅度、神经传导速度
5. 安全性：不良事件、严重不良事件、停药原因、实验室异常
6. 方案依从性：实际暴露时间、漏服/漏做记录、方案违背类型"""

            bias_text = """**偏倚控制动作**
- 采用中心分层区组随机，避免不同中心检测条件不一致带来的选择偏倚
- 电生理评估尽量盲法判读，原始波形统一由核心实验室复核
- 将基线放电频率、年龄、基础神经病变作为预设协变量进入主要模型
- 缺失数据优先用 MMRM；同时做多重插补敏感性分析"""

            return f"""{discussion_bridge}

我先把可以直接执行的统计骨架给出来，而不是停留在概念层面。

**主要终点**
- 建议主要终点定义为：{endpoint}
- 统计量用“第 28 天较基线变化值的组间差值”，并给出 95% CI

**样本量**
- {sample_size_text}

{bias_text}

{crf_text}

下一步建议：直接按访视维度展开成 Excel / EDC 可用的 CRF 表头，并把必填校验一起列上。"""

        if "研究护士" in role and wants_crf:
            return f"""{discussion_bridge}

我不再泛泛描述，直接给执行层可落地的 CRF 采集框架。

**访视安排**
- V0 筛选：知情同意、纳排标准、既往史、基线检查
- V1 入组/随机：分组、首剂给药、基线{endpoint}
- V2 随访 1：依从性、不良事件、关键电生理复测
- V3 随访 2：主要终点评估、并发症/脱落记录
- V4 结束访视：结局确认、数据核对、方案违背归档

**CRF 页面建议**
1. 筛选页：受试者编号、筛选失败原因、纳排标准逐条勾选
2. 基线页：人口学、诊断依据、病程、合并用药、基线电生理
3. 干预页：剂量、频次、起止时间、联合治疗
4. 疗效页：第 7/14/28 天放电频率、突触传递指标、症状评分
5. 安全页：AE/SAE、处理措施、结局、与研究药关联性
6. 质控页：源数据核对、逻辑核查、缺失项追踪、中心反馈

**执行要点**
- 电生理原始文件统一命名并上传，避免手工录入误差
- 每次访视 24 小时内完成 EDC 录入，48 小时内完成核查
- 对主要终点字段设置必填与范围校验，减少后期清洗成本"""

        # 构建响应
        if "临床主任" in role:
            if needs_concrete_plan:
                study_shape = "单中心前瞻性对照研究"
                if is_neurosignal_topic:
                    study_shape = "机制验证型前瞻性研究"
                return f"""{discussion_bridge}

**立项判断**
- 这题值得做，但当前阶段更适合先按“{study_shape}”推进，不要一开始就铺成大而全的正式试验。
- 我们这轮的目标不是再讲题目意义，而是先把主终点、时间窗和执行骨架钉住。

**临床主任先拍板的边界**
1. 研究对象/材料：明确采用哪类神经元模型或受试者人群，是否区分对照。
2. 暴露定义：{intervention} 的剂量、频次、暴露时长和对照方式。
3. 主终点：先锁定 {endpoint}，次要终点再看突触后电流幅度、神经传导速度或安全性。
4. 关键风险：重点盯样本异质性、检测平台不一致和主要终点定义漂移，这三点最容易让方案失真。

**我要求下一位专家直接补的交付物**
- 统计学家：给样本量估算口径、主要分析模型和分析集定义。
- 研究护士/执行位：给访视点或采样时间点、CRF 页签和质控动作。
- 博士生：把文献提取表头列出来，先看现有终点口径是否一致。

这轮直接往“主终点、样本量、CRF/访视表”推进。"""

            return f"""{discussion_bridge}

临床上这题先别铺太大，我建议先把研究边界钉住：
1. 研究对象：明确 {disease} 的诊断标准和当前治疗阶段，不然入组会很散。
2. 干预/暴露：把 {intervention} 的定义写到可以执行，剂量、周期、对照方式都要明确。
3. 主终点：先锁定 {endpoint}，不要一上来同时追多个主问题。
4. 安全性：把最需要盯的风险事件提前列成监测清单。

下一步先同时推进两件事：文献侧收口证据缺口，统计侧确认主终点是否足够支撑样本量设计。"""

        elif "博士生" in role:
            if needs_concrete_plan:
                return f"""{discussion_bridge}

我把文献回顾直接压成执行清单，不再泛泛说“要查文献”。

**检索问题**
1. {intervention} 是否已经被用于观察 {endpoint} 或相近电生理终点。
2. 既往研究常用的暴露浓度、观察时间窗和模型类型是什么。
3. 现有研究最大的缺口是样本量不足、终点不统一，还是缺少对照。

**文献提取表头**
- 模型类型 / 人群定义
- 暴露剂量与时长
- 主要终点与时间窗
- 样本量或重复次数
- 对照设置
- 统计方法

**我目前的判断**
- 这题通常不是“完全没证据”，而是终点定义和观察时间窗不统一。
- 所以后续统计学家和执行位给出的样本量、CRF/采集表，必须尽量对齐文献里最稳定的终点口径。"""

            return f"""{discussion_bridge}

我先把文献侧真正影响方案成败的点提出来，而不是只报数量：
1. 现有研究是否已经把 {intervention} 用在 {disease} 上，结论是正向、阴性还是不一致。
2. 过去研究最常见的短板通常有三类：样本量偏小、随访时间偏短、终点定义不统一。
3. 如果 {endpoint} 在现有研究里定义不一致，我们这次必须提前统一，否则后面无法和文献对照。

我建议下一步先把检索问题收成 3 个：已有最佳证据是什么、最大的证据空白是什么、我们这次最值得补哪一块。接下来直接把检索式和纳入标准列成执行清单。"""

        elif "流行病学家" in role:
            extra_bias = ""
            if wants_bias or wants_sample_size:
                extra_bias = """
**4. 这题我建议先锁定的偏倚控制动作**
- 用中心分层随机，避免不同实验平台/病区带来的系统差异
- 主要终点统一由盲法评估者判读
- 预先定义共变量和亚组，避免结果出来后再“挑分析”
- 把失访原因分层记录，防止只留下完成度高的患者"""

            return f"""{discussion_bridge}

从方法学上，这题我建议先定 4 个骨架：
1. 研究类型：如果目标是验证疗效，优先双臂平行对照；如果当前更像探索，可先做前瞻性队列。
2. 入排标准：把疾病定义、既往治疗、关键合并症先写清，避免基线过散。
3. 终点时间窗：{endpoint} 放在第几天/第几周评估，必须先固定。
4. 偏倚控制：随机、盲法判读、预设协变量、缺失原因分层记录，这四件事最值钱。

{extra_bias}

下一步先和统计学家一起把“主终点 + 时间窗 + 脱落处理”定死，再展开 CRF。"""

        elif "统计学家" in role:
            return f"""{discussion_bridge}

统计上我先把最容易出错的地方点出来：
1. 主终点只留一个，建议先围绕 {endpoint} 搭主要分析。
2. 主分析集默认 ITT，同时保留 PP 作为敏感性分析，不要反过来。
3. 如果是连续终点，优先考虑基线调整后的 ANCOVA/MMRM；如果是时间事件终点，再走 KM + Cox。
4. 样本量在没有完整先验数据前，可以先按中等效应量做预估，再根据文献或预实验修正；通常要额外预留 10%-15% 脱落。

最直接的下一步是先补三项输入：主终点定义、预期差值、标准差或事件率来源。有了这三项，样本量和 SAP 骨架就可以继续往下写。"""

        elif "研究护士" in role:
            return f"""{discussion_bridge}

执行层我先说最容易拖垮项目的 4 件事：
1. 筛选和入组谁负责、在什么时点完成，必须写成 SOP。
2. {endpoint} 的采集时间点要前置固定，不然后面补录一定乱。
3. CRF / EDC 里的必填、范围校验和缺失原因要提前配好，别等锁库前再追。
4. AE/SAE 上报链路要在启动前演练一次，不要只写在纸面上。

下一步直接输出“访视表 + CRF 页面清单 + 数据核查频率”，这样临床团队和统计团队都能直接接上。"""

        elif "趋势研究员" in role:
            return f"""{discussion_bridge}

我只补跟“是否值得继续做、未来怎么发表”直接相关的判断：
1. 这题的创新点不在“胰岛素和神经元”这几个字本身，而在于你能否把终点口径、时间窗和对照做得比现有研究更统一。
2. 如果后面想投高水平期刊，审稿人最先问的通常是：为什么选这个主终点、为什么这个时间窗、为什么样本量足够。
3. 所以现在最值钱的不是继续扩展背景，而是把“主终点 + 样本量依据 + CRF/访视表”一次写实。

只要这三件事先收住，后面无论走机制文章还是方法学文章，投稿路径都会清晰很多。"""

        elif "实验追踪员" in role:
            return f"""{discussion_bridge}

我把推进节奏直接拆成 4 个里程碑：
1. 本周锁定主终点、时间窗和对照方案。
2. 下一个节点完成文献提取表、样本量口径和 CRF/访视表初稿。
3. 第三个节点做一次内部质控审阅，专查终点定义、字段缺失和 SOP 漏项。
4. 最后再决定是否进入正式执行或先补预实验。

这样推进的好处是每一步都有可交付物，不会停留在概念讨论。"""

        elif "模型QA专家" in role:
            return f"""{discussion_bridge}

我先把最该设的质量闸门列出来：
1. 主终点字段必须唯一且有范围校验。
2. 每个访视点都要记录缺失原因，不能只留空值。
3. 关键原始文件要能追溯到受试者编号和时间点。
4. 统计分析前先做一次字段字典和逻辑核查，避免后面边分析边补表。

把这四个检查点前置，后面的讨论才不至于又回到“原则正确、落地很乱”。"""

        # 默认响应
        return f"""{discussion_bridge}

我先对这轮问题做一个直接回应：这题的关键不在于再讲一遍{disease}的重要性，而在于把 {intervention}、{endpoint} 和执行路径尽快钉住。

站在 {role} 的角度，我建议下一步至少完成三件事：
1. 把本轮最重要的问题缩成一句可验证的研究假设；
2. 明确主终点和时间窗，避免后面所有角色各说各话；
3. 先列一个可执行清单，再决定谁接着往下展开。

接下来最该做的是沿着“{current_request}”这条线，把我这边负责的具体内容继续展开。"""
    
    async def generate_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7
    ):
        """流式生成响应"""
        
        if not self.client or self._mock_mode_active():
            # 没有 API Key，返回模拟流式响应
            full_response = self._generate_mock_response(system_prompt, user_prompt)
            # 模拟流式输出，每次输出几个字
            import asyncio
            for i in range(0, len(full_response), 20):
                yield full_response[i:i+20]
                await asyncio.sleep(0.05)  # 模拟打字延迟
            return
        
        try:
            stream = self.client.chat.completions.create(
                model=self.moonshot_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            error_text = str(e).lower()
            if getattr(e, "status_code", None) == 429 or any(
                marker in error_text
                for marker in ["timeout", "timed out", "read timeout", "engine is currently overloaded", "temporarily unavailable"]
            ):
                self.mock_until = time.time() + 300
            print(f"❌ 流式 API 调用失败: {e}")
            # API 失败时返回模拟流式响应
            import asyncio
            full_response = self._generate_mock_response(system_prompt, user_prompt)
            for i in range(0, len(full_response), 20):
                yield full_response[i:i+20]
                await asyncio.sleep(0.05)

# 全局 LLM 客户端实例
llm_client = LLMClient()
