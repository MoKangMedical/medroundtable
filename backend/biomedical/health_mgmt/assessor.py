"""Health Assessment Engine — MediSlim core"""
from typing import Any, Dict, List, Optional

CONDITIONS = {
    "glp1_weight": {"name":"GLP-1减重评估","questions":[
        {"id":"bmi","text":"BMI值","type":"numeric"},
        {"id":"diet_attempts","text":"过去尝试过几种减肥方法","type":"numeric"},
        {"id":"comorbidities","text":"是否有糖尿病/高血压","type":"yesno"}]},
    "hair_loss": {"name":"脱发评估","questions":[
        {"id":"onset","text":"脱发开始时间","type":"text","options":["3个月内","6个月-1年","1年以上"]},
        {"id":"pattern","text":"脱发模式","type":"text","options":["弥漫性","前额后退","头顶稀疏","斑片状"]},
        {"id":"family","text":"家族脱发史","type":"yesno"}]},
    "skin": {"name":"皮肤问题评估","questions":[
        {"id":"type","text":"主要皮肤问题","type":"text","options":["痤疮","湿疹","银屑病","色斑","老化"]},
        {"id":"duration","text":"持续时间","type":"text","options":["1周内","1-3个月","半年以上"]}]},
    "sleep": {"name":"睡眠质量评估","questions":[
        {"id":"latency","text":"入睡时间","type":"text","options":["<15分钟","15-30分钟","30-60分钟",">1小时"]},
        {"id":"awakenings","text":"夜间醒来次数","type":"numeric"},
        {"id":"duration","text":"每晚实际睡眠时间","type":"text","options":["<4小时","4-6小时","6-8小时"]}]},
    "male": {"name":"男性健康评估","questions":[
        {"id":"age","text":"年龄","type":"numeric"},
        {"id":"fatigue","text":"疲劳程度","type":"text","options":["无","轻度","中度","重度"]},
        {"id":"libido","text":"性欲变化","type":"text","options":["正常","轻度下降","明显下降"]}]},
}

INTERACTIONS = {
    ("华法林","阿司匹林"): {"severity":"high","note":"增加出血风险"},
    ("华法林","布洛芬"): {"severity":"high","note":"增加出血风险"},
    ("二甲双胍","造影剂"): {"severity":"high","note":"需停药48h"},
    ("ACE抑制剂","钾补充剂"): {"severity":"moderate","note":"监测血钾"},
    ("他汀类","红霉素"): {"severity":"moderate","note":"横纹肌溶解风险"},
}


class HealthAssessor:
    def list_conditions(self): return [{"id":k,"name":v["name"],"questions":len(v["questions"])} for k,v in CONDITIONS.items()]
    def get_questionnaire(self, cid): return CONDITIONS.get(cid)
    def assess(self, cid: str, answers: Dict) -> Dict:
        sev = "low"
        if cid == "glp1_weight":
            bmi = float(answers.get("bmi",25))
            sev = "high" if bmi>30 else "moderate" if bmi>28 else "low"
        elif cid == "sleep":
            lat = answers.get("latency","<15分钟")
            sev = "high" if lat in ["30-60分钟",">1小时"] else "moderate" if lat=="15-30分钟" else "low"
        elif cid == "hair_loss":
            fam = answers.get("family",False)
            pat = answers.get("pattern","")
            sev = "high" if fam and pat in ["前额后退","头顶稀疏"] else "moderate" if fam or pat in ["前额后退","头顶稀疏"] else "low"
        costs = {"low":199,"moderate":699,"high":1694}
        durs = {"low":"1个月","moderate":"3个月","high":"6个月"}
        return {"condition":cid,"severity":sev,"cost":costs[sev],"duration":durs[sev]}


class PrescriptionChecker:
    def check(self, drugs: List[str]) -> Dict:
        inter = []
        for i,d1 in enumerate(drugs):
            for d2 in drugs[i+1:]:
                k = (d1,d2) if (d1,d2) in INTERACTIONS else (d2,d1)
                if k in INTERACTIONS:
                    info = INTERACTIONS[k]
                    inter.append({"drug1":d1,"drug2":d2,"severity":info["severity"],"note":info["note"]})
        hi = sum(1 for i in inter if i["severity"]=="high")
        return {"drugs":drugs,"interactions":inter,"safety":"danger" if hi>0 else "caution" if inter else "safe"}


assessor = HealthAssessor()
rx_checker = PrescriptionChecker()
