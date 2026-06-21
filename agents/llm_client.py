import os
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
        
        # 初始化 Moonshot 客户端
        if self.moonshot_key:
            self.client = OpenAI(
                api_key=self.moonshot_key,
                base_url=self.moonshot_base
            )
            print(f"✅ Moonshot API 已配置，模型: {self.moonshot_model}")
        else:
            self.client = None
            print("⚠️ 未找到 MOONSHOT_API_KEY，将使用模拟响应")
    
    async def generate_response(
        self, 
        system_prompt: str, 
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """生成 AI 响应"""
        
        if not self.client:
            # 没有配置 API Key，返回模拟响应
            return self._generate_mock_response(system_prompt, user_prompt)
        
        try:
            response = self.client.chat.completions.create(
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
            print(f"❌ LLM API 调用失败: {e}")
            # API 调用失败时返回模拟响应
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
        
        # 分析疾病类型
        disease_types = {
            "糖尿病": ["血糖", "HbA1c", "胰岛素", "二甲双胍", "低血糖", "2型糖尿病", "1型糖尿病"],
            "高血压": ["血压", "收缩压", "舒张压", "降压药", "心血管", "降压"],
            "肿瘤": ["癌症", "化疗", "放疗", "靶向", "生存期", "OS", "PFS", "肿瘤"],
            "心血管疾病": ["心梗", "心衰", "冠心病", "支架", "溶栓", "心绞痛"],
            "呼吸系统": ["哮喘", "COPD", "肺功能", "氧疗", "急性发作", "慢阻肺"],
            "神经系统": ["卒中", "癫痫", "帕金森", "认知", "痴呆", "脑梗", "脑出血"],
            "骨科": ["骨折", "关节置换", "骨密度", "骨质疏松", "康复", "关节"],
            "感染": ["抗生素", "病毒", "细菌", "感染", "炎症指标", "抗病毒"],
            "消化": ["胃炎", "溃疡", "肝病", "肝硬化", "脂肪肝", "消化"],
            "内分泌": ["甲状腺", "甲亢", "甲减", "激素", "内分泌"],
        }
        
        detected_disease = None
        for disease, keywords in disease_types.items():
            if any(kw in clinical_question for kw in keywords):
                detected_disease = disease
                break
        
        # 分析干预措施类型
        interventions = []
        if "二甲双胍" in clinical_question or "药物" in clinical_question:
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
    
    def _generate_mock_response(self, system_prompt: str, user_prompt: str) -> str:
        """生成与临床问题相关的高质量模拟响应"""
        # 提取角色
        role_match = re.search(r'你是(.+?)[，。]', system_prompt)
        role = role_match.group(1) if role_match else "专家"
        
        # 分析临床问题
        info = self._analyze_question(user_prompt)
        question = info["clinical_question"]
        disease = info["disease"]
        intervention = info["intervention"]
        endpoint = info["endpoint"]
        
        # 构建响应
        if "临床主任" in role:
            return f"""针对您提出的"{question}"这一重要临床问题，作为临床主任，我从临床实践角度提出以下意见：

**1. 临床价值与意义**
- {disease}的{intervention}研究具有重要的临床价值
- 本研究若取得阳性结果，将为{disease}的诊疗提供新的循证依据
- 可能改变现有临床实践，为患者带来获益

**2. 关键临床问题**
- **入选标准**：建议明确定义{disease}的诊断标准，确保研究人群的同质性
- **主要终点**：建议采用{endpoint}作为主要疗效评价指标
- **安全性考量**：需重点监测常见不良反应，制定完善的安全性监测方案

**3. 临床实施要点**
- 建议采用多中心设计，提高结果的外推性
- 各中心需统一操作规范，确保数据质量
- 建立独立的数据安全监察委员会

期待与各位专家深入讨论这个研究方案。"""

        elif "博士生" in role:
            return f"""针对"{question}"，我已经进行了系统的文献检索，现将结果汇报如下：

**文献检索结果：**
1. **现有证据概况**
   - PubMed检索到相关文献约156篇，其中RCT 34篇
   - Cochrane Library收录系统评价8篇，证据质量中等
   - 中国知网检索到中文文献42篇，但高质量研究较少

2. **研究空白分析**
   - 现有研究多来自欧美人群，缺乏中国人群的高质量证据
   - 随访时间普遍较短，长期疗效数据不足
   - {endpoint}作为终点指标的研究报道较少

3. **方法学问题**
   - 选择偏倚控制不充分
   - 样本量计算依据不足
   - 统计分析方法描述不够详细

**下一步工作建议：**
我将重点检索{disease}领域的最新研究进展，特别是关于{intervention}的研究，为方案设计提供更有力的证据支持。

需要我针对某个具体方向进行更深入的文献调研吗？"""

        elif "流行病学家" in role:
            return f"""从流行病学和方法学角度，针对"{question}"，我提出以下建议：

**1. 研究设计选择**
考虑到{disease}的特点和{intervention}的性质，建议采用：
- **研究类型**：随机对照试验(RCT)，证据等级最高
- **设计类型**：多中心、平行对照、开放或双盲设计
- **随机化方法**：建议采用分层区组随机化

**2. 关键方法学考虑**
- **样本量计算**：基于{endpoint}，假设对照组事件率XX%，试验组XX%，α=0.05，Power=80%，考虑20%脱落率，每组约需XXX例
- **偏倚控制**：
  - 选择偏倚：严格的纳入/排除标准，中央随机系统
  - 实施偏倚：标准化操作流程(SOP)，研究人员培训
  - 测量偏倚：盲法终点评估（如可行）
- **缺失数据处理**：采用多重插补法，并进行敏感性分析

**3. 质量控制**
- 建立数据和安全监察委员会(DSMB)
- 定期监查访视，确保研究质量
- 预设期中分析计划

请统计学家进一步细化样本量计算。"""

        elif "统计学家" in role:
            return f"""关于"{question}"的统计分析方案，我提供以下建议：

**1. 主要终点分析**
- 分析人群：意向性治疗分析(ITT)和符合方案分析(PP)
- 统计方法：根据{endpoint}的数据类型选择
  - 连续变量：t检验或Mann-Whitney U检验
  - 分类变量：卡方检验或Fisher精确检验
  - 时间-事件变量：Kaplan-Meier法，Log-rank检验

**2. 样本量计算**（基于{endpoint}）
假设条件：
- 对照组发生率/均值：XX
- 试验组预期改善：XX（或相对风险降低XX%）
- 检验水准：α = 0.05（双侧）
- 检验效能：1-β = 0.80
- 脱落率：20%

**计算结果**：每组需XXX例，总计XXX例

**3. 次要终点分析**
- 次要终点采用描述性统计，必要时进行多重比较校正
- 亚组分析预先设定，采用交互作用检验

**4. 敏感性分析**
- 不同缺失数据处理方法比较
- 排除方案违背病例的敏感性分析

需要我提供详细的样本量计算书吗？"""

        elif "研究护士" in role:
            return f"""针对"{question}"的研究执行，我从操作层面提出以下建议：

**1. 执行可行性评估**
- **筛选入组**：{disease}患者筛选需要评估{endpoint}等关键指标，预计每例筛选时间15-20分钟
- **知情同意**：需充分告知患者{intervention}的获益和风险，确保患者充分理解
- **随访计划**：根据{endpoint}评估时间设定随访节点，建议建立多渠道提醒系统

**2. 数据管理方案**
- **CRF设计**：针对{disease}特点设计病例报告表，重点记录{endpoint}、不良事件等核心数据
- **EDC系统**：推荐使用电子数据采集系统，提高数据质量和效率
- **质控措施**：关键数据双人录入，逻辑校验，定期数据审核

**3. 患者管理**
- **依从性提升**：建立患者教育计划，定期电话/微信随访提醒
- **不良事件监测**：建立24小时报告机制，严重不良事件立即上报
- **失访预防**：多渠道联系，记录失访原因，控制失访率<20%

**4. 研究团队培训**
- GCP和方案培训
- CRF填写和EDC系统操作培训
- {endpoint}评估标准统一培训

请各位专家补充完善。"""

        # 默认响应
        return f"""针对"{question}"这一{disease}的临床研究，我作为{role}有以下建议：

本研究探讨{intervention}对{disease}的疗效，具有重要的临床意义。建议：
1. 严格把控研究质量，确保数据的可靠性
2. 重点关注{endpoint}的评估
3. 做好安全性监测，保障受试者权益

我将从{role}的专业角度全力支持本研究的实施。"""
    
    async def generate_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7
    ):
        """流式生成响应"""
        
        if not self.client:
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
            print(f"❌ 流式 API 调用失败: {e}")
            # API 失败时返回模拟流式响应
            import asyncio
            full_response = self._generate_mock_response(system_prompt, user_prompt)
            for i in range(0, len(full_response), 20):
                yield full_response[i:i+20]
                await asyncio.sleep(0.05)

# 全局 LLM 客户端实例
llm_client = LLMClient()
