"""Rare Disease Diagnostic Engine — MediChat-RD core"""
from typing import Any, Dict, List, Optional

DISEASE_DB = {
    "SMA": {"name":"脊髓性肌萎缩症","gene":"SMN1","inheritance":"AR","prevalence":"1/10000",
            "symptoms":["肌无力","肌萎缩","运动发育迟缓","吞咽困难","呼吸困难"],
            "tests":["SMN1基因检测","SMN蛋白水平","肌电图"],"treatments":["诺西那生钠","Zolgensma","利司扑兰"],"category":"神经肌肉"},
    "DMD": {"name":"杜氏肌营养不良","gene":"DMD","inheritance":"XR","prevalence":"1/3500男婴",
            "symptoms":["进行性肌无力","腓肠肌假性肥大","Gowers征","心肌病","智力下降"],
            "tests":["CK酶检测","DMD基因检测","肌肉活检"],"treatments":["激素治疗","外显子跳跃疗法"],"category":"神经肌肉"},
    "Wilson": {"name":"肝豆状核变性","gene":"ATP7B","inheritance":"AR","prevalence":"1/30000",
               "symptoms":["肝功能异常","精神症状","K-F环","震颤","构音障碍"],
               "tests":["铜蓝蛋白","24h尿铜","ATP7B基因"],"treatments":["青霉胺","锌剂","肝移植"],"category":"代谢性"},
    "FD": {"name":"法布雷病","gene":"GLA","inheritance":"XR","prevalence":"1/40000",
           "symptoms":["肢端疼痛","少汗","血管角质瘤","心肌肥厚","蛋白尿"],
           "tests":["α-GalA活性","GLA基因","Gb3水平"],"treatments":["酶替代治疗","分子伴侣疗法"],"category":"溶酶体贮积"},
    "PKU": {"name":"苯丙酮尿症","gene":"PAH","inheritance":"AR","prevalence":"1/10000",
            "symptoms":["智力障碍","癫痫","湿疹","鼠臭味","色素减少"],
            "tests":["血苯丙氨酸","PAH基因","尿有机酸"],"treatments":["低苯丙氨酸饮食","BH4补充"],"category":"氨基酸代谢"},
    "SLE": {"name":"系统性红斑狼疮","gene":"多基因","inheritance":"复杂","prevalence":"1/1000",
            "symptoms":["蝶形红斑","关节痛","光敏","口腔溃疡","肾炎","血液异常"],
            "tests":["ANA","抗dsDNA","补体C3/C4"],"treatments":["羟氯喹","糖皮质激素","免疫抑制剂"],"category":"自身免疫"},
}

SYMPTOM_INDEX = {}
for did, info in DISEASE_DB.items():
    for s in info["symptoms"]:
        SYMPTOM_INDEX.setdefault(s, []).append(did)


class RareDiseaseEngine:
    def search_by_symptoms(self, symptoms: List[str], top_k: int = 5) -> List[Dict]:
        scores = {}
        for s in symptoms:
            for did in SYMPTOM_INDEX.get(s, []):
                scores[did] = scores.get(did, 0) + 1
        results = []
        for did, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]:
            info = DISEASE_DB[did].copy()
            info["id"] = did
            info["match_score"] = score
            results.append(info)
        return results

    def get_disease(self, did: str) -> Optional[Dict]:
        info = DISEASE_DB.get(did)
        if info: r = info.copy(); r["id"] = did; return r
        return None

    def list_diseases(self, category: Optional[str] = None) -> List[Dict]:
        return [{"id":k,"name":v["name"],"category":v.get("category","")}
                for k,v in DISEASE_DB.items() if not category or v.get("category","").startswith(category)]

    def differential(self, symptoms: List[str]) -> Dict[str, Any]:
        cands = self.search_by_symptoms(symptoms, 10)
        tests = set()
        for c in cands: tests.update(c.get("tests",[]))
        top = cands[0] if cands else {}
        conf = "high" if top and top.get("match_score",0) >= 3 else "moderate" if top else "low"
        return {"diagnoses":cands,"recommended_tests":list(tests),"confidence":conf,"symptom_count":len(symptoms)}


rare_engine = RareDiseaseEngine()
