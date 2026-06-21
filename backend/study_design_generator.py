from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from typing import List, Dict
from datetime import datetime
import os
import re

class StudyDesignGenerator:
    """智能研究设计生成器"""
    
    def __init__(self):
        pass
    
    def extract_study_design_from_messages(self, messages: List[Dict], clinical_question: str) -> Dict:
        """从讨论消息中提取研究设计要素"""
        
        design = {
            "title": "",
            "study_type": "随机对照试验(RCT)",
            "background": clinical_question,
            "objectives": {
                "primary": "",
                "secondary": []
            },
            "study_design": {
                "design_type": "多中心、随机、双盲、平行对照试验",
                "randomization": "区组随机化，1:1分配",
                "blinding": "双盲设计",
                "duration": "预计12个月"
            },
            "population": {
                "inclusion": [],
                "exclusion": [],
                "sample_size": 0
            },
            "intervention": {
                "experimental": "",
                "control": "安慰剂对照"
            },
            "endpoints": {
                "primary": "",
                "secondary": [],
                "safety": ["不良事件发生率", "严重不良事件", "实验室检查异常"]
            },
            "statistics": {
                "sample_size_calculation": "",
                "analysis_population": "ITT/PP",
                "statistical_methods": "",
                "significance_level": "双侧α=0.05",
                "power": "80%"
            },
            "ethical_considerations": [
                "伦理委员会审批",
                "知情同意",
                "数据保密",
                "受试者权益保护"
            ],
            "timeline": {
                "preparation": "3个月",
                "recruitment": "6个月",
                "follow_up": "12个月",
                "data_analysis": "3个月",
                "total": "约24个月"
            }
        }
        
        # 从讨论内容中提取关键信息
        for msg in messages:
            content = msg.get('content', '')
            role = msg.get('from_role', '')
            
            # 提取样本量
            sample_size_match = re.search(r'(\d+)\s*例', content)
            if sample_size_match:
                design['population']['sample_size'] = int(sample_size_match.group(1))
            
            # 提取纳入标准
            if '纳入' in content or '入选' in content:
                inclusion_items = re.findall(r'[\d\.]\s*([^。\n]+(?:年龄|诊断|病程|同意)[^。\n]*)', content)
                if inclusion_items:
                    design['population']['inclusion'] = inclusion_items[:5]
            
            # 提取排除标准
            if '排除' in content:
                exclusion_items = re.findall(r'[\d\.]\s*([^。\n]+(?:过敏|严重|妊娠|哺乳)[^。\n]*)', content)
                if exclusion_items:
                    design['population']['exclusion'] = exclusion_items[:5]
            
            # 提取主要终点
            if '主要终点' in content or 'primary endpoint' in content.lower():
                primary_match = re.search(r'主要终点[：:]([^。\n]+)', content)
                if primary_match:
                    design['endpoints']['primary'] = primary_match.group(1).strip()
            
            # 提取干预措施
            if '试验组' in content or '治疗组' in content:
                exp_match = re.search(r'试验组[：:]([^。\n]+)', content)
                if exp_match:
                    design['intervention']['experimental'] = exp_match.group(1).strip()
            
            # 统计专家的建议
            if role == 'statistician':
                # 提取显著性水平和效能
                alpha_match = re.search(r'α[=＝](\d+\.?\d*)', content)
                if alpha_match:
                    design['statistics']['significance_level'] = f"双侧α={alpha_match.group(1)}"
                
                power_match = re.search(r'效能|power[=＝]?(\d+)%', content, re.IGNORECASE)
                if power_match:
                    design['statistics']['power'] = f"{power_match.group(1)}%"
        
        # 如果没有提取到，使用默认值
        if not design['population']['inclusion']:
            design['population']['inclusion'] = [
                "符合疾病诊断标准",
                "年龄18-75岁",
                "知情同意并签署知情同意书"
            ]
        
        if not design['population']['exclusion']:
            design['population']['exclusion'] = [
                "对研究药物过敏",
                "严重肝肾功能不全",
                "妊娠或哺乳期妇女"
            ]
        
        if not design['endpoints']['primary']:
            design['endpoints']['primary'] = "主要疗效指标的变化"
        
        if design['population']['sample_size'] == 0:
            design['population']['sample_size'] = 200
        
        if not design['intervention']['experimental']:
            design['intervention']['experimental'] = "试验药物治疗"
        
        return design
    
    def generate_complete_protocol(self, design: Dict) -> str:
        """生成完整的研究方案文本"""
        
        protocol = f"""
# 临床研究方案

## 研究标题
{design.get('title', '待定')}

## 一、研究背景
{design.get('background', '')}

## 二、研究目的

### 2.1 主要目的
{design['objectives']['primary'] or '评价试验药物的有效性和安全性'}

### 2.2 次要目的
"""
        
        for i, obj in enumerate(design['objectives']['secondary'] or ['探索亚组疗效差异', '评价生活质量改善', '评估经济学效益'], 1):
            protocol += f"{i}. {obj}\n"
        
        protocol += f"""
## 三、研究设计

### 3.1 设计类型
{design['study_design']['design_type']}

### 3.2 随机化方法
{design['study_design']['randomization']}

### 3.3 盲法
{design['study_design']['blinding']}

### 3.4 研究周期
{design['study_design']['duration']}

## 四、研究人群

### 4.1 纳入标准
"""
        
        for i, criteria in enumerate(design['population']['inclusion'], 1):
            protocol += f"{i}. {criteria}\n"
        
        protocol += "\n### 4.2 排除标准\n"
        
        for i, criteria in enumerate(design['population']['exclusion'], 1):
            protocol += f"{i}. {criteria}\n"
        
        protocol += f"""
### 4.3 样本量
计划纳入{design['population']['sample_size']}例受试者（试验组和对照组各{design['population']['sample_size']//2}例）

## 五、干预措施

### 5.1 试验组
{design['intervention']['experimental']}

### 5.2 对照组
{design['intervention']['control']}

## 六、研究终点

### 6.1 主要终点
{design['endpoints']['primary']}

### 6.2 次要终点
"""
        
        for i, endpoint in enumerate(design['endpoints']['secondary'] or ['次要疗效指标', '生活质量评分', '患者报告结局'], 1):
            protocol += f"{i}. {endpoint}\n"
        
        protocol += "\n### 6.3 安全性终点\n"
        
        for i, endpoint in enumerate(design['endpoints']['safety'], 1):
            protocol += f"{i}. {endpoint}\n"
        
        protocol += f"""
## 七、统计分析

### 7.1 样本量计算
基于以下假设：
- 显著性水平：{design['statistics']['significance_level']}
- 检验效能：{design['statistics']['power']}
- 脱落率：预计15%

### 7.2 分析人群
{design['statistics']['analysis_population']}

### 7.3 统计方法
{design['statistics']['statistical_methods'] or '采用描述性统计、组间比较、生存分析等'}

## 八、伦理考虑
"""
        
        for i, consideration in enumerate(design['ethical_considerations'], 1):
            protocol += f"{i}. {consideration}\n"
        
        protocol += f"""
## 九、研究时间线

- 准备阶段：{design['timeline']['preparation']}
- 受试者招募：{design['timeline']['recruitment']}
- 随访期：{design['timeline']['follow_up']}
- 数据分析：{design['timeline']['data_analysis']}
- 总周期：{design['timeline']['total']}

## 十、数据管理

### 10.1 数据收集
采用电子数据采集系统(EDC)，确保数据的准确性、完整性和及时性。

### 10.2 质量控制
- 研究者培训
- 标准操作规程(SOP)
- 定期监查访视
- 数据审核

### 10.3 数据安全
建立数据安全监测委员会(DSMB)，定期评估研究安全性数据。

---

*本方案由MedRoundTable AI医学科研协作平台自动生成*
*生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}*
"""
        
        return protocol

# 生成器实例
study_design_generator = StudyDesignGenerator()
