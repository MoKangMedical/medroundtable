from typing import Dict, List, Optional
from datetime import datetime

class StudyTemplates:
    """研究方案模板库"""
    
    TEMPLATES = {
        "rct": {
            "name": "随机对照试验 (RCT)",
            "description": "金标准研究设计，用于评估干预措施的有效性和安全性",
            "sections": {
                "title": "【研究标题】",
                "background": """【研究背景】
本研究旨在评估[干预措施]对[目标人群]的[主要结局]的影响。

前期研究基础：
- 
- 

研究创新性：
- 
""",
                "objectives": """【研究目的】
主要目的：
评估[干预措施]对[主要结局指标]的影响。

次要目的：
1. 
2. 
3. 
""",
                "study_design": """【研究设计】
设计类型：多中心/单中心、随机、双盲/单盲、平行对照试验

随机化方法：
- 分层区组随机化
- 随机化比例：1:1
- 随机化中心：[中心名称]

盲法：
- 受试者：盲
- 研究者：盲
- 统计分析：盲
""",
                "population": """【研究人群】
纳入标准：
1. 年龄18-75岁
2. 符合[疾病]诊断标准
3. 
4. 自愿参加并签署知情同意书

排除标准：
1. 对研究药物过敏
2. 严重肝肾功能不全
3. 妊娠或哺乳期妇女
4. 近3个月内参加过其他临床试验
""",
                "intervention": """【干预措施】
试验组：
- 药物：[药物名称]
- 剂量：
- 给药途径：
- 疗程：

对照组：
- 药物：[安慰剂/阳性对照]
- 剂量：
- 给药途径：
- 疗程：
""",
                "endpoints": """【研究终点】
主要终点：
[具体定义和测量方法]

次要终点：
1. 
2. 
3. 

安全性终点：
- 不良事件发生率
- 严重不良事件
- 实验室检查异常
""",
                "statistics": """【统计分析】
样本量计算：
- 显著性水平：α=0.05（双侧）
- 把握度：1-β=0.80
- 预期效应量：
- 脱落率：15%
- 需要样本量：试验组___例，对照组___例

统计方法：
- 主要分析：ITT分析
- 统计检验：
- 多因素分析：
- 亚组分析：
"""
            }
        },
        
        "cohort": {
            "name": "前瞻性队列研究",
            "description": "观察性研究，用于评估暴露因素与结局的关联",
            "sections": {
                "title": "【研究标题】",
                "background": """【研究背景】
本研究是一项前瞻性队列研究，旨在探讨[暴露因素]与[疾病结局]之间的关系。

研究意义：
- 
- 

前期研究：
- 
""",
                "objectives": """【研究目的】
主要目的：
评估[暴露因素]与[疾病发生]的关联。

次要目的：
1. 识别其他危险因素
2. 建立预测模型
3. 
""",
                "study_design": """【研究设计】
设计类型：前瞻性、观察性队列研究

研究现场：
- [医院/社区名称]
- 入组时间：[开始时间] 至 [结束时间]
- 随访时间：__年
""",
                "population": """【研究人群】
暴露组纳入标准：
1. [明确的暴露定义]
2. 年龄__-__岁
3. 

非暴露组纳入标准：
1. 无[暴露因素]
2. 其他条件同暴露组

排除标准（两组相同）：
1. 已患有[研究疾病]
2. 
3. 预期寿命<__年
""",
                "exposure": """【暴露评估】
暴露定义：
[详细的暴露定义和判定标准]

暴露测量：
- 测量工具：
- 测量时点：
- 质量控制：
""",
                "followup": """【随访计划】
随访频率：
- 基线：
- 第3个月：
- 第6个月：
- 第12个月：
-  thereafter 每__个月

随访内容：
- 疾病发生情况
- 暴露状态变化
- 混杂因素变化
- 失访情况
""",
                "statistics": """【统计分析】
样本量计算：
- 预期发病率（暴露组）：___%
- 预期发病率（非暴露组）：___%
- α=0.05，Power=80%
- 需要样本量：暴露组___例，非暴露组___例

统计方法：
- 累积发病率计算
- 相对危险度（RR）及95%CI
- 归因危险度（AR）
- Cox比例风险模型
- 倾向性评分匹配
"""
            }
        },
        
        "case_control": {
            "name": "病例对照研究",
            "description": "回顾性研究，用于罕见疾病的危险因素探索",
            "sections": {
                "title": "【研究标题】",
                "background": """【研究背景】
本研究采用病例对照设计，探索[疾病]的危险因素。

研究必要性：
- [疾病]发病率低，队列研究不可行
- 潜伏期长，前瞻性研究周期长
- 
""",
                "objectives": """【研究目的】
主要目的：
识别[疾病]的独立危险因素。

探索性目的：
1. 评估暴露-剂量反应关系
2. 识别高危人群特征
3. 
""",
                "study_design": """【研究设计】
设计类型：医院/人群基础的病例对照研究

病例来源：
- [医院名称] [科室]
- 诊断时间：[起始] 至 [结束]
- 诊断标准：[具体标准]

对照来源：
- 同一医院同期非[研究疾病]患者
- 社区人群
- 匹配因素：[年龄/性别/等]
""",
                "population": """【研究对象】
病例组纳入标准：
1. 经[诊断标准]确诊的[疾病]患者
2. 诊断时间在[时间段]
3. 年龄__-__岁
4. 知情同意

对照组纳入标准：
1. 同期就诊/调查的[匹配条件]人群
2. 无[研究疾病]病史
3. 其他条件同病例组

排除标准：
1. 无法回忆暴露史
2. 
""",
                "exposure": """【暴露评估】
暴露定义：
[危险因素的定义]

暴露测量：
- 测量方式：问卷/访谈/病历回顾
- 暴露时点：[疾病诊断前__年]
- 暴露分级：
  * 无暴露
  * 轻度暴露
  * 中度暴露
  * 重度暴露
""",
                "statistics": """【统计分析】
样本量计算：
- 预期暴露率（对照组）：___%
- 预期OR值：___
- α=0.05，Power=80%
- 病例:对照 = 1:__
- 需要样本量：病例___例，对照___例

统计方法：
- 描述性统计
- 卡方检验/t检验
- 单因素/多因素Logistic回归
- 计算OR及95%CI
- 分层分析
- 交互作用检验
"""
            }
        },
        
        "cross_sectional": {
            "name": "横断面研究",
            "description": "描述疾病/暴露的分布，用于患病率调查",
            "sections": {
                "title": "【研究标题】",
                "background": """【研究背景】
本研究旨在调查[疾病/健康状况]在[目标人群]中的分布特征。

调查意义：
- 了解疾病负担
- 识别高危人群
- 为后续研究提供基线数据
""",
                "objectives": """【研究目的】
主要目的：
估计[目标人群]中[疾病]的患病率。

次要目的：
1. 描述疾病分布特征
2. 分析相关因素
3. 
""",
                "study_design": """【研究设计】
设计类型：横断面调查

研究现场：
- [具体地点]
- 调查时间：[起始] 至 [结束]

抽样方法：
- 目标人群：[定义]
- 抽样框：[来源]
- 抽样方法：多阶段分层随机抽样
- 样本量：___人
""",
                "population": """【研究人群】
纳入标准：
1. 年龄__-__岁
2. [地区]常住居民
3. 居住时间≥__年
4. 同意参与调查

排除标准：
1. 严重认知障碍
2. 无法配合调查
3. 
""",
                "measurements": """【测量内容】
1. 问卷调查
   - 人口学特征
   - 生活方式
   - 疾病史
   - 

2. 体格检查
   - 身高、体重、BMI
   - 血压
   - 

3. 实验室检查
   - 
   - 
""",
                "statistics": """【统计分析】
样本量计算：
- 预期患病率：___%
- 容许误差：δ=___%
- α=0.05
- 设计效应：deff=___
- 需要样本量：___人

统计方法：
- 患病率计算（点估计+95%CI）
- 加权调整
- 复杂抽样设计方差估计
- 亚组比较
"""
            }
        }
    }
    
    @classmethod
    def get_template_list(cls) -> List[Dict]:
        """获取所有模板列表"""
        return [
            {
                "id": key,
                "name": template["name"],
                "description": template["description"]
            }
            for key, template in cls.TEMPLATES.items()
        ]
    
    @classmethod
    def get_template(cls, template_id: str) -> Optional[Dict]:
        """获取指定模板"""
        return cls.TEMPLATES.get(template_id)
    
    @classmethod
    def generate_protocol(cls, template_id: str, custom_data: Dict) -> str:
        """
        根据模板生成完整研究方案
        
        Args:
            template_id: 模板ID
            custom_data: 自定义数据，用于填充模板
        
        Returns:
            完整的研究方案文本
        """
        template = cls.get_template(template_id)
        if not template:
            return "模板不存在"
        
        sections = template["sections"]
        
        # 合并所有章节
        protocol = f"""# {template['name']}研究方案

## 研究基本信息
- 研究类型：{template['name']}
- 生成时间：{datetime.now().strftime('%Y年%m月%d日')}
- 使用模板：{template_id}

---

"""
        
        for section_name, section_content in sections.items():
            protocol += section_content + "\n\n"
        
        return protocol
    
    @classmethod
    def recommend_template(cls, clinical_question: str) -> List[Dict]:
        """
        根据临床问题推荐合适的模板
        
        简单规则：
        - 包含"随机""对照""试验" → RCT
        - 包含"队列""随访""前瞻性" → 队列研究
        - 包含"病例对照""危险因素" → 病例对照
        - 其他 → 横断面
        """
        question_lower = clinical_question.lower()
        
        recommendations = []
        
        if any(word in question_lower for word in ['随机', '对照', '试验', '干预', '治疗']):
            recommendations.append({
                "id": "rct",
                "name": "随机对照试验 (RCT)",
                "reason": "您的研究涉及干预措施评估，RCT是金标准设计",
                "confidence": "高"
            })
        
        if any(word in question_lower for word in ['队列', '随访', '前瞻', '观察', '发生']):
            recommendations.append({
                "id": "cohort",
                "name": "前瞻性队列研究",
                "reason": "您的研究关注暴露与疾病的关联，适合队列研究",
                "confidence": "高"
            })
        
        if any(word in question_lower for word in ['病例对照', '危险', '因素', '罕见']):
            recommendations.append({
                "id": "case_control",
                "name": "病例对照研究",
                "reason": "您的研究适合探索罕见疾病的危险因素",
                "confidence": "高"
            })
        
        # 默认推荐横断面
        if not recommendations:
            recommendations.append({
                "id": "cross_sectional",
                "name": "横断面研究",
                "reason": "适合描述疾病分布和患病率调查",
                "confidence": "中"
            })
        
        return recommendations


# 全局实例
templates = StudyTemplates()
