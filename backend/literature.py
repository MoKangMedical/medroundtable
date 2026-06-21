import requests
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET
from datetime import datetime

class LiteratureSearch:
    """文献检索服务 - 支持PubMed"""
    
    def __init__(self):
        self.pubmed_base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.email = "medroundtable@research.com"  # PubMed要求提供邮箱
    
    def search_pubmed(
        self, 
        query: str, 
        max_results: int = 10,
        sort: str = "relevance"
    ) -> Dict:
        """
        搜索PubMed文献
        
        Args:
            query: 搜索关键词
            max_results: 最大返回数量
            sort: 排序方式 (relevance/date)
        
        Returns:
            {
                "total_count": int,
                "articles": [
                    {
                        "pmid": str,
                        "title": str,
                        "abstract": str,
                        "authors": List[str],
                        "journal": str,
                        "pub_date": str,
                        "doi": str
                    }
                ]
            }
        """
        try:
            # 第一步：搜索获取PMID列表
            search_url = f"{self.pubmed_base}/esearch.fcgi"
            search_params = {
                "db": "pubmed",
                "term": query,
                "retmax": max_results,
                "sort": sort,
                "retmode": "json",
                "email": self.email
            }
            
            search_response = requests.get(search_url, params=search_params, timeout=30)
            search_data = search_response.json()
            
            id_list = search_data.get("esearchresult", {}).get("idlist", [])
            total_count = int(search_data.get("esearchresult", {}).get("count", 0))
            
            if not id_list:
                return {
                    "total_count": 0,
                    "articles": [],
                    "query": query
                }
            
            # 第二步：获取详细信息
            articles = self._fetch_article_details(id_list)
            
            return {
                "total_count": total_count,
                "articles": articles,
                "query": query
            }
            
        except Exception as e:
            print(f"PubMed搜索失败: {e}")
            return {
                "total_count": 0,
                "articles": [],
                "query": query,
                "error": str(e)
            }
    
    def _fetch_article_details(self, pmids: List[str]) -> List[Dict]:
        """获取文章详细信息"""
        try:
            fetch_url = f"{self.pubmed_base}/efetch.fcgi"
            fetch_params = {
                "db": "pubmed",
                "id": ",".join(pmids),
                "retmode": "xml",
                "email": self.email
            }
            
            response = requests.get(fetch_url, params=fetch_params, timeout=30)
            root = ET.fromstring(response.content)
            
            articles = []
            for article in root.findall(".//PubmedArticle"):
                article_data = self._parse_article(article)
                if article_data:
                    articles.append(article_data)
            
            return articles
            
        except Exception as e:
            print(f"获取文章详情失败: {e}")
            return []
    
    def _parse_article(self, article_elem) -> Optional[Dict]:
        """解析XML文章数据"""
        try:
            # PMID
            pmid_elem = article_elem.find(".//PMID")
            pmid = pmid_elem.text if pmid_elem is not None else ""
            
            # 标题
            title_elem = article_elem.find(".//ArticleTitle")
            title = title_elem.text if title_elem is not None else ""
            
            # 摘要
            abstract_elems = article_elem.findall(".//AbstractText")
            abstract = " ".join([elem.text for elem in abstract_elems if elem.text])
            
            # 作者
            authors = []
            author_list = article_elem.findall(".//Author")
            for author in author_list[:5]:  # 只取前5个作者
                lastname = author.find("LastName")
                forename = author.find("ForeName")
                if lastname is not None:
                    name = lastname.text
                    if forename is not None:
                        name = f"{lastname.text} {forename.text}"
                    authors.append(name)
            
            # 期刊
            journal_elem = article_elem.find(".//Title")
            journal = journal_elem.text if journal_elem is not None else ""
            
            # 发表日期
            date_elem = article_elem.find(".//PubDate/Year")
            pub_date = date_elem.text if date_elem is not None else ""
            
            # DOI
            doi_elem = article_elem.find(".//ArticleId[@IdType='doi']")
            doi = doi_elem.text if doi_elem is not None else ""
            
            return {
                "pmid": pmid,
                "title": title,
                "abstract": abstract[:500] + "..." if len(abstract) > 500 else abstract,
                "authors": authors,
                "journal": journal,
                "pub_date": pub_date,
                "doi": doi,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            }
            
        except Exception as e:
            print(f"解析文章失败: {e}")
            return None
    
    def search_by_clinical_question(self, question: str) -> Dict:
        """根据临床问题自动构建搜索词并检索"""
        # 简单的关键词提取（实际可以使用LLM优化）
        # 移除常见停用词
        stop_words = {'的', '了', '和', '是', '在', '有', '我', '与', '对', '及', '等', '为', '中', '上', '从', '到', '一个'}
        words = question.split()
        keywords = [w for w in words if w not in stop_words][:5]  # 取前5个关键词
        
        query = " AND ".join(keywords)
        return self.search_pubmed(query, max_results=10)
    
    def get_related_articles(self, pmid: str, max_results: int = 5) -> List[Dict]:
        """获取相关文献"""
        try:
            elink_url = f"{self.pubmed_base}/elink.fcgi"
            params = {
                "dbfrom": "pubmed",
                "db": "pubmed",
                "id": pmid,
                "cmd": "neighbor",
                "retmode": "json",
                "email": self.email
            }
            
            response = requests.get(elink_url, params=params, timeout=30)
            data = response.json()
            
            # 提取相关文章ID
            related_ids = []
            if "linksets" in data and len(data["linksets"]) > 0:
                for linkset in data["linksets"]:
                    if "linksetdbs" in linkset:
                        for linksetdb in linkset["linksetdbs"]:
                            if "links" in linksetdb:
                                related_ids.extend(linksetdb["links"][:max_results])
            
            if related_ids:
                return self._fetch_article_details(related_ids)
            return []
            
        except Exception as e:
            print(f"获取相关文献失败: {e}")
            return []


# 全局实例
literature_search = LiteratureSearch()
