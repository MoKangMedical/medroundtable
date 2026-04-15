"""Drug Database Engine — DrugBank-style compound lookup"""
from typing import Any, Dict, List, Optional

DRUGS = {
    "semaglutide": {"name":"司美格鲁肽","brand":"Ozempic/Wegovy","target":"GLP-1R",
                    "indication":["T2DM","肥胖"],"mechanism":"GLP-1受体激动剂",
                    "dosage":"每周0.25-2.4mg","side_effects":["恶心","呕吐","腹泻","胰腺炎风险"],
                    "approval":"FDA 2017","category":"内分泌"},
    "metformin": {"name":"二甲双胍","brand":"Glucophage","target":"AMPK/mTOR",
                  "indication":["T2DM"],"mechanism":"减少肝糖输出，增加胰岛素敏感性",
                  "dosage":"500-2550mg/日","side_effects":["胃肠不适","乳酸酸中毒(罕见)","B12缺乏"],
                  "approval":"FDA 1994","category":"内分泌"},
    "nusinersen": {"name":"诺西那生钠","brand":"Spinraza","target":"SMN2",
                   "indication":["SMA"],"mechanism":"SMN2前体mRNA剪接修饰",
                   "dosage":"12mg鞘内注射","side_effects":["头痛","恶心","血小板减少"],
                   "approval":"FDA 2016","category":"神经科"},
    "pembrolizumab": {"name":"帕博利珠单抗","brand":"Keytruda","target":"PD-1",
                      "indication":["黑色素瘤","NSCLC","MSI-H肿瘤"],"mechanism":"PD-1检查点抑制剂",
                      "dosage":"200mg Q3W","side_effects":["免疫相关AE","疲劳","皮疹"],
                      "approval":"FDA 2014","category":"肿瘤"},
    "risdiplam": {"name":"利司扑兰","brand":"Evrysdi","target":"SMN2",
                  "indication":["SMA"],"mechanism":"SMN2前体mRNA剪接修饰",
                  "dosage":"5mg口服每日一次","side_effects":["发热","腹泻","皮疹"],
                  "approval":"FDA 2020","category":"神经科"},
}


class DrugDatabase:
    def search(self, query: str) -> List[Dict]:
        results = []
        for did, d in DRUGS.items():
            if query.lower() in did or query.lower() in d["name"] or query.lower() in d.get("brand","").lower():
                r = d.copy(); r["id"] = did; results.append(r)
        return results

    def get(self, drug_id: str) -> Optional[Dict]:
        d = DRUGS.get(drug_id)
        if d: r = d.copy(); r["id"] = drug_id; return r
        return None

    def list_all(self, category: Optional[str] = None) -> List[Dict]:
        return [{"id":k,"name":v["name"],"brand":v.get("brand",""),"category":v.get("category","")}
                for k,v in DRUGS.items() if not category or v.get("category","") == category]

    def by_target(self, target: str) -> List[Dict]:
        return [{"id":k,**v} for k,v in DRUGS.items() if target.lower() in v.get("target","").lower()]


drug_db = DrugDatabase()
