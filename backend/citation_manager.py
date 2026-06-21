from typing import List, Dict
import re

class CitationManager:
    """文献引用管理器"""
    
    def __init__(self):
        self.citations = []
        self.citation_counter = 0
        
        # 模拟文献数据库（实际应用中应连接真实数据库）
        self.reference_database = {
            "糖尿病": [
                {
                    "id": "ref1",
                    "authors": "UK Prospective Diabetes Study Group",
                    "title": "Intensive blood-glucose control with sulphonylureas or insulin compared with conventional treatment and risk of complications in patients with type 2 diabetes",
                    "journal": "Lancet",
                    "year": 1998,
                    "volume": "352",
                    "pages": "837-853",
                    "doi": "10.1016/S0140-6736(98)07019-6"
                },
                {
                    "id": "ref2", 
                    "authors": "American Diabetes Association",
                    "title": "Standards of Medical Care in Diabetes—2023",
                    "journal": "Diabetes Care",
                    "year": 2023,
                    "volume": "46",
                    "issue": "Suppl 1",
                    "pages": "S1-S291",
                    "doi": "10.2337/dc23-Srev"
                },
                {
                    "id": "ref3",
                    "authors": "Zheng Y, Ley SH, Hu FB",
                    "title": "Global aetiology and epidemiology of type 2 diabetes mellitus and its complications",
                    "journal": "Nat Rev Endocrinol",
                    "year": 2018,
                    "volume": "14",
                    "pages": "88-98",
                    "doi": "10.1038/nrendo.2017.151"
                }
            ],
            "二甲双胍": [
                {
                    "id": "ref4",
                    "authors": "Sanchez-Rangel E, Inzucchi SE",
                    "title": "Metformin: Clinical Use in Type 2 Diabetes",
                    "journal": "Diabetologia",
                    "year": 2017,
                    "volume": "60",
                    "pages": "1586-1593",
                    "doi": "10.1007/s00125-017-4336-x"
                },
                {
                    "id": "ref5",
                    "authors": "Foretz M, Guigas B, Bertrand L, et al.",
                    "title": "Metformin: from mechanisms of action to therapies",
                    "journal": "Cell Metab",
                    "year": 2014,
                    "volume": "20",
                    "pages": "953-966",
                    "doi": "10.1016/j.cmet.2014.09.018"
                }
            ],
            "随机对照试验": [
                {
                    "id": "ref6",
                    "authors": "Schulz KF, Altman DG, Moher D",
                    "title": "CONSORT 2010 Statement: updated guidelines for reporting parallel group randomised trials",
                    "journal": "BMJ",
                    "year": 2010,
                    "volume": "340",
                    "pages": "c332",
                    "doi": "10.1136/bmj.c332"
                },
                {
                    "id": "ref7",
                    "authors": "Moher D, Hopewell S, Schulz KF, et al.",
                    "title": "CONSORT 2010 explanation and elaboration: updated guidelines for reporting parallel group randomised trials",
                    "journal": "BMJ",
                    "year": 2010,
                    "volume": "340",
                    "pages": "c869",
                    "doi": "10.1136/bmj.c869"
                }
            ],
            "样本量": [
                {
                    "id": "ref8",
                    "authors": "Julious SA",
                    "title": "Sample size of 12 per group rule of thumb for a pilot study",
                    "journal": "Pharm Stat",
                    "year": 2005,
                    "volume": "4",
                    "pages": "287-291",
                    "doi": "10.1002/pst.185"
                }
            ],
            "统计分析": [
                {
                    "id": "ref9",
                    "authors": "Altman DG",
                    "title": "Practical Statistics for Medical Research",
                    "journal": "Chapman and Hall/CRC",
                    "year": 1991,
                    "pages": "611",
                    "doi": ""
                }
            ]
        }
    
    def find_relevant_references(self, content: str) -> List[Dict]:
        """根据内容查找相关文献"""
        relevant_refs = []
        
        # 关键词匹配
        for keyword, refs in self.reference_database.items():
            if keyword in content:
                for ref in refs:
                    # 避免重复
                    if ref not in relevant_refs:
                        relevant_refs.append(ref)
        
        return relevant_refs
    
    def add_citations_to_content(self, content: str, role: str) -> tuple:
        """为内容添加引用标记，返回（带引用的内容，引用列表）"""
        
        # 查找相关文献
        refs = self.find_relevant_references(content)
        
        if not refs:
            return content, []
        
        # 根据角色选择最相关的1-2篇文献
        selected_refs = refs[:2]
        
        # 添加引用标记
        citation_marks = []
        for i, ref in enumerate(selected_refs, 1):
            self.citation_counter += 1
            ref['number'] = self.citation_counter
            citation_marks.append(f"[{self.citation_counter}]")
        
        # 在内容末尾添加引用标记
        if citation_marks:
            # 在段落合适位置插入引用
            sentences = content.split('。')
            if len(sentences) > 2:
                # 在中间句子后插入引用
                insert_pos = len(sentences) // 2
                sentences[insert_pos] = sentences[insert_pos] + citation_marks[0]
                if len(citation_marks) > 1 and len(sentences) > 3:
                    sentences[-2] = sentences[-2] + citation_marks[1]
                content = '。'.join(sentences)
            else:
                content = content + ' ' + citation_marks[0]
        
        return content, selected_refs
    
    def get_all_citations(self) -> List[Dict]:
        """获取所有引用文献的格式化列表"""
        sorted_refs = sorted(self.citations, key=lambda x: x.get('number', 0))
        return sorted_refs
    
    def format_citation(self, ref: Dict) -> str:
        """格式化单条引用为文本"""
        authors = ref.get('authors', '')
        title = ref.get('title', '')
        journal = ref.get('journal', '')
        year = ref.get('year', '')
        volume = ref.get('volume', '')
        pages = ref.get('pages', '')
        doi = ref.get('doi', '')
        
        citation_text = f"{authors}. {title}. {journal}"
        if year:
            citation_text += f" {year}"
        if volume:
            citation_text += f";{volume}"
        if pages:
            citation_text += f":{pages}"
        if doi:
            citation_text += f". doi:{doi}"
        
        return citation_text
    
    def generate_reference_list(self) -> str:
        """生成完整的参考文献列表"""
        if not self.citations:
            return ""
        
        ref_list = "## 参考文献\n\n"
        for ref in sorted(self.citations, key=lambda x: x.get('number', 0)):
            ref_list += f"[{ref.get('number', '')}] {self.format_citation(ref)}\n\n"
        
        return ref_list
    
    def reset(self):
        """重置引用管理器"""
        self.citations = []
        self.citation_counter = 0

# 全局引用管理器实例
citation_manager = CitationManager()
