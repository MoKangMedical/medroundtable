"""
Rare Disease Diagnostic Engine
Adapted from MediChat-RD for medroundtable integration
"""
from typing import Any, Dict, List, Optional
import logging
import json

logger = logging.getLogger(__name__)


class RareDiseaseEngine:
    """Knowledge-graph-driven rare disease diagnosis engine."""

    def __init__(self):
        self.disease_db = {}
        self.symptom_index = {}
        self._load_disease_data()

    def _load_disease_data(self):
        """Load rare disease reference data."""
        self.disease_db = {
            "SMA": {
                "name": "脊髓性肌萎缩症",
                "name_en": "Spinal Muscular Atrophy",
                "gene": "SMN1",
                "inheritance": "常染色体隐性",
                "prevalence": "1/10000",
                "symptoms": ["肌无力", "肌萎缩", "运动发育迟缓", "吞咽困难", "呼吸困难"],
                "key_tests": ["SMN1基因检测", "SMN蛋白水平", "肌电图"],
                "treatments": ["诺西那生钠(Nusinersen)", "Zolgensma", "利司扑兰(Risdiplam)"],
                "category": "神经肌肉疾病"
            },
            "DMD": {
                "name": "杜氏肌营养不良",
                "name_en": "Duchenne Muscular Dystrophy",
                "gene": "DMD",
                "inheritance": "X连锁隐性",
                "prevalence": "1/3500男婴",
                "symptoms": ["进行性肌无力", "腓肠肌假性肥大", "Gowers征", "心肌病", "智力下降"],
                "key_tests": ["CK酶检测", "DMD基因检测", "肌肉活检"],
                "treatments": ["激素治疗", "外显子跳跃疗法", "基因治疗"],
                "category": "神经肌肉疾病"
            },
            "Wilson": {
                "name": "肝豆状核变性",
                "name_en": "Wilson Disease",
                "gene": "ATP7B",
                "inheritance": "常染色体隐性",
                "prevalence": "1/30000",
                "symptoms": ["肝功能异常", "精神症状", "K-F环", "震颤", "构音障碍"],
                "key_tests": ["血清铜蓝蛋白", "24h尿铜", "肝铜定量", "ATP7B基因检测"],
                "treatments": ["青霉胺", "锌剂", "肝移植"],
                "category": "代谢性疾病"
            },
            "FD": {
                "name": "法布雷病",
                "name_en": "Fabry Disease",
                "gene": "GLA",
                "inheritance": "X连锁隐性",
                "prevalence": "1/40000-1/117000",
                "symptoms": ["肢端疼痛", "少汗", "血管角质瘤", "心肌肥厚", "蛋白尿"],
                "key_tests": ["α-半乳糖苷酶A活性", "GLA基因检测", "Gb3水平"],
                "treatments": ["酶替代治疗(阿加糖酶)", "分子伴侣疗法"],
                "category": "溶酶体贮积症"
            },
            "PKU": {
                "name": "苯丙酮尿症",
                "name_en": "Phenylketonuria",
                "gene": "PAH",
                "inheritance": "常染色体隐性",
                "prevalence": "1/10000",
                "symptoms": ["智力障碍", "癫痫", "湿疹", "鼠臭味", "色素减少"],
                "key_tests": ["血苯丙氨酸", "PAH基因检测", "尿有机酸"],
                "treatments": ["低苯丙氨酸饮食", "BH4补充", "Pegvaliase"],
                "category": "氨基酸代谢病"
            }
        }

        # Build symptom index
        for did, info in self.disease_db.items():
            for symptom in info["symptoms"]:
                self.symptom_index.setdefault(symptom, []).append(did)

    def search_by_symptoms(self, symptoms: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search diseases by symptoms with relevance scoring."""
        scores = {}
        for symptom in symptoms:
            matched = self.symptom_index.get(symptom, [])
            for did in matched:
                scores[did] = scores.get(did, 0) + 1

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        results = []
        for did, score in ranked[:top_k]:
            info = self.disease_db[did].copy()
            info["id"] = did
            info["match_score"] = score
            info["match_ratio"] = f"{score}/{len(info['symptoms'])}"
            results.append(info)
        return results

    def get_disease(self, disease_id: str) -> Optional[Dict[str, Any]]:
        """Get full disease information."""
        info = self.disease_db.get(disease_id)
        if info:
            result = info.copy()
            result["id"] = disease_id
            return result
        return None

    def list_diseases(self, category: Optional[str] = None) -> List[Dict[str, str]]:
        """List all diseases, optionally filtered by category."""
        results = []
        for did, info in self.disease_db.items():
            if category and info.get("category") != category:
                continue
            results.append({"id": did, "name": info["name"], "name_en": info["name_en"], "category": info.get("category", "")})
        return results

    def differential_diagnosis(self, symptoms: List[str], age: Optional[int] = None, gender: Optional[str] = None) -> Dict[str, Any]:
        """Perform differential diagnosis analysis."""
        candidates = self.search_by_symptoms(symptoms, top_k=10)

        # Generate diagnostic plan
        all_tests = set()
        for c in candidates:
            all_tests.update(c.get("key_tests", []))

        return {
            "differential_diagnoses": candidates,
            "recommended_tests": list(all_tests),
            "symptom_count": len(symptoms),
            "candidate_count": len(candidates),
            "diagnostic_confidence": "high" if (candidates and candidates[0].get("match_ratio", "").startswith("5/")) else "moderate" if candidates else "low",
        }


rare_disease_engine = RareDiseaseEngine()
