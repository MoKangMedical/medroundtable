"""
ADMET主引擎
整合毒性、PK、合成可及性预测，输出综合ADMET报告
"""

import logging
from dataclasses import dataclass, asdict
from typing import Optional

from .toxicity import ToxicityPredictor
from .pk_predictor import PKPredictor
from .sa_score import SAScorer

logger = logging.getLogger(__name__)


@dataclass
class ADMETReport:
    """ADMET综合报告"""
    smiles: str
    absorption: dict         # 吸收: caco2, hia, bioavailability
    distribution: dict       # 分布: bbb, ppbr, vd
    metabolism: dict         # 代谢: cyp_inhibitors, cyp_substrate
    excretion: dict          # 排泄: clearance, half_life
    toxicity: dict           # 毒性: herg, ames, ld50, dili
    synthesis: dict          # 合成: sa_score, synthetic_accessibility
    overall: dict            # 综合评分
    pass_filter: bool        # 是否通过筛选
    recommendation: str      # pass / warning / reject


class ADMETEngine:
    """
    ADMET预测引擎
    SMILES → 全面ADMET评估
    """

    # ADMET筛选阈值
    THRESHOLDS = {
        "caco2": 0,           # log(cm/s) > -5.15
        "hia": 0.3,           # HIA > 30%
        "bbb": -0.5,          # BBB渗透性
        "herg_ic50": 10,      # hERG IC50 > 10 μM (安全)
        "ames": 0.5,          # Ames阴性概率
        "ld50": 2.5,          # log(mol/kg) > 2.5
        "sa_score": 6,        # SA Score < 6
    }

    def __init__(self):
        self.tox = ToxicityPredictor()
        self.pk = PKPredictor()
        self.sa = SAScorer()

    def predict(self, smiles: str) -> ADMETReport:
        """
        对单个分子进行全ADMET预测
        """
        # 吸收
        absorption = {
            "caco2_permeability": self.pk.predict_caco2(smiles),
            "hia": self.pk.predict_hia(smiles),
            "oral_bioavailability": self.pk.predict_bioavailability(smiles),
            "pgp_substrate": self.pk.predict_pgp(smiles),
        }

        # 分布
        distribution = {
            "bbb_penetration": self.pk.predict_bbb(smiles),
            "ppbr": self.pk.predict_ppbr(smiles),
            "vd": self.pk.predict_vd(smiles),
        }

        # 代谢
        metabolism = {
            "cyp1a2_inhibitor": self.tox.predict_cyp_inhibition(smiles, "1A2"),
            "cyp2c9_inhibitor": self.tox.predict_cyp_inhibition(smiles, "2C9"),
            "cyp2d6_inhibitor": self.tox.predict_cyp_inhibition(smiles, "2D6"),
            "cyp3a4_inhibitor": self.tox.predict_cyp_inhibition(smiles, "3A4"),
            "cyp2c19_inhibitor": self.tox.predict_cyp_inhibition(smiles, "2C19"),
        }

        # 排泄
        excretion = {
            "clearance": self.pk.predict_clearance(smiles),
            "half_life": self.pk.predict_half_life(smiles),
        }

        # 毒性
        toxicity = {
            "herg_inhibition": self.tox.predict_herg(smiles),
            "ames_mutagenicity": self.tox.predict_ames(smiles),
            "ld50": self.tox.predict_ld50(smiles),
            "dili": self.tox.predict_dili(smiles),
            "cardiotoxicity_risk": self.tox.predict_cardiotoxicity(smiles),
        }

        # 合成
        sa_result = self.sa.score(smiles)
        synthesis = {
            "sa_score": sa_result["sa_score"],
            "synthetic_accessibility": sa_result["accessibility"],
            "n_steps_estimate": sa_result["n_steps"],
        }

        # 综合评分
        overall = self._calc_overall(absorption, distribution, metabolism, excretion, toxicity, synthesis)

        # 通过性判断
        pass_filter = self._apply_filters(absorption, toxicity, synthesis)
        recommendation = "pass" if pass_filter else \
            "warning" if overall["total_score"] > 0.4 else "reject"

        return ADMETReport(
            smiles=smiles,
            absorption=absorption,
            distribution=distribution,
            metabolism=metabolism,
            excretion=excretion,
            toxicity=toxicity,
            synthesis=synthesis,
            overall=overall,
            pass_filter=pass_filter,
            recommendation=recommendation,
        )

    def batch_predict(self, smiles_list: list[str]) -> list[dict]:
        """批量ADMET预测"""
        results = []
        for smiles in smiles_list:
            try:
                report = self.predict(smiles)
                results.append(asdict(report))
            except Exception as e:
                logger.warning(f"ADMET预测失败 ({smiles[:30]}): {e}")
                results.append({"smiles": smiles, "error": str(e)})
        return results

    def _calc_overall(self, absorption, distribution, metabolism, excretion, toxicity, synthesis) -> dict:
        """计算综合ADMET评分"""
        scores = {}

        # 吸收分
        abs_score = 0.5
        if absorption["caco2_permeability"] > -5.15:
            abs_score += 0.2
        if absorption["hia"] > 0.5:
            abs_score += 0.2
        if absorption["oral_bioavailability"] > 0.3:
            abs_score += 0.1
        scores["absorption"] = min(abs_score, 1.0)

        # 分布分
        dist_score = 0.5 + (0.2 if distribution["ppbr"] < 0.95 else 0)
        scores["distribution"] = min(dist_score, 1.0)

        # 代谢分（抑制越少越好）
        met_inhibitors = sum(1 for k, v in metabolism.items() if v < 0.5)
        scores["metabolism"] = min(0.3 + met_inhibitors * 0.15, 1.0)

        # 毒性分（越低越好）
        tox_score = 0.8
        if toxicity["herg_inhibition"] < 0.5:
            tox_score -= 0.1
        if toxicity["ames_mutagenicity"] > 0.5:
            tox_score -= 0.2
        if toxicity["dili"] > 0.5:
            tox_score -= 0.2
        scores["toxicity"] = max(tox_score, 0.1)

        # 合成分
        sa = synthesis["sa_score"]
        scores["synthesis"] = max(0, 1 - (sa - 1) / 9)

        # 总分
        scores["total_score"] = round(
            scores["absorption"] * 0.25 +
            scores["distribution"] * 0.15 +
            scores["metabolism"] * 0.15 +
            scores["toxicity"] * 0.30 +
            scores["synthesis"] * 0.15, 3
        )

        return {k: round(v, 3) for k, v in scores.items()}

    def _apply_filters(self, absorption, toxicity, synthesis) -> bool:
        """硬性筛选规则"""
        # 吸收必须可接受
        if absorption["caco2_permeability"] < -5.5:
            return False
        # hERG不能太高
        if toxicity["herg_inhibition"] > 0.8:
            return False
        # 合成不能太难
        if synthesis["sa_score"] > 8:
            return False
        return True
