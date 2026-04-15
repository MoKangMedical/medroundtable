"""
全流程编排器
靶点发现→虚拟筛选→分子生成→先导优化→ADMET评估的完整Pipeline

改进(v2.1): 添加halt-on-failure决策检查点
- 关键阶段(靶点/筛选/生成)失败时终止Pipeline
- 非关键阶段(ADMET/优化)失败时仅警告并继续
- 每个阶段之间有输入验证检查点
- 错误信息显式记录到PipelineResult
"""

import logging
import json
from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import Optional

from openai import OpenAI

logger = logging.getLogger(__name__)

# 阶段关键性定义: critical阶段失败会终止pipeline, non-critical仅警告
CRITICAL_STAGES = {"target_discovery", "virtual_screening", "molecular_generation"}
NON_CRITICAL_STAGES = {"admet_prediction", "lead_optimization"}


@dataclass
class PipelineConfig:
    """Pipeline配置"""
    disease: str
    target: str = ""
    target_chembl_id: str = ""
    max_papers: int = 30
    max_compounds: int = 500
    n_generate: int = 100
    n_optimize: int = 30
    top_n: int = 10
    use_docking: bool = False
    auto_mode: bool = True  # 全自动模式
    halt_on_critical_failure: bool = True  # 关键阶段失败是否终止


@dataclass
class PipelineResult:
    """Pipeline执行结果"""
    disease: str
    target: str
    stages_completed: list[str]
    target_report: Optional[dict] = None
    screening_report: Optional[dict] = None
    generation_report: Optional[dict] = None
    optimization_report: Optional[dict] = None
    admet_reports: list[dict] = field(default_factory=list)
    final_candidates: list[dict] = field(default_factory=list)
    execution_time: float = 0.0
    timestamp: str = ""
    errors: list[dict] = field(default_factory=list)  # 显式错误记录
    halted: bool = False  # 是否因关键失败而终止
    halt_reason: str = ""  # 终止原因


class PipelineOrchestrator:
    """
    全流程编排器
    一键执行从靶点到候选药物的完整流程
    """

    def __init__(
        self,
        llm_client: Optional[OpenAI] = None,
        llm_model: str = "mimo-v2-pro"
    ):
        self.llm = llm_client
        self.model = llm_model

    def run_full_pipeline(self, config: PipelineConfig) -> PipelineResult:
        """执行完整pipeline（v2.1: 含halt-on-failure决策检查点）"""
        start_time = datetime.now()
        stages = []

        logger.info(f"""
╔══════════════════════════════════════════════╗
║  MediPharma 全流程Pipeline v2.1              ║
║  疾病: {config.disease:<37s} ║
║  靶点: {(config.target or '待发现'):<37s} ║
║  模式: {'全自动' if config.auto_mode else '交互式':<36s} ║
╚══════════════════════════════════════════════╝
        """)

        result = PipelineResult(
            disease=config.disease,
            target=config.target,
            stages_completed=[],
            timestamp=start_time.isoformat()
        )

        # ========== Stage 1: 靶点发现 (关键阶段) ==========
        if not config.target:
            logger.info("📍 Stage 1: 靶点发现 [CRITICAL]")
            try:
                from target_discovery.engine import TargetDiscoveryEngine
                td = TargetDiscoveryEngine(llm_client=self.llm, llm_model=self.model)
                report = td.discover_targets(
                    disease=config.disease,
                    max_papers=config.max_papers,
                    top_n=config.top_n
                )
                result.target_report = asdict(report)
                stages.append("target_discovery")

                # 自动选择Top靶点
                if config.auto_mode and report.top_targets:
                    config.target = report.top_targets[0]["gene_symbol"]
                    result.target = config.target
                    logger.info(f"✅ 自动选择靶点: {config.target}")
                else:
                    # 检查点: 靶点发现成功但无结果
                    err = {"stage": "target_discovery", "error": "未找到候选靶点", "severity": "critical"}
                    result.errors.append(err)
                    logger.error(f"❌ 靶点发现完成但无候选靶点")
                    if config.halt_on_critical_failure:
                        result.halted = True
                        result.halt_reason = "靶点发现未产生候选靶点"
                        return self._finalize(result, stages, start_time)
            except Exception as e:
                err = {"stage": "target_discovery", "error": str(e), "severity": "critical"}
                result.errors.append(err)
                logger.error(f"❌ 靶点发现失败: {e}")
                if config.halt_on_critical_failure:
                    result.halted = True
                    result.halt_reason = f"靶点发现异常: {e}"
                    return self._finalize(result, stages, start_time)
        else:
            stages.append("target_discovery (pre-specified)")
            logger.info(f"✅ 靶点预设: {config.target}")

        # 检查点: 验证靶点就绪
        if not config.target:
            logger.error("❌ 无有效靶点，Pipeline终止")
            result.halted = True
            result.halt_reason = "Stage 1→2 检查点失败: 无有效靶点"
            return self._finalize(result, stages, start_time)

        # ========== Stage 2: 虚拟筛选 (关键阶段) ==========
        logger.info(f"📍 Stage 2: 虚拟筛选 (靶点: {config.target}) [CRITICAL]")
        try:
            from virtual_screening.engine import VirtualScreeningEngine
            vs = VirtualScreeningEngine()
            screening = vs.screen(
                target_chembl_id=config.target_chembl_id or config.target,
                max_compounds=config.max_compounds,
                top_n=config.top_n,
                use_docking=config.use_docking
            )
            result.screening_report = asdict(screening)
            stages.append("virtual_screening")

            # 检查点: 筛选是否产生有效结果
            screened = result.screening_report.get("total_screened", 0)
            if screened == 0:
                logger.warning("⚠️ 虚拟筛选未筛到化合物，但继续（分子生成可补充）")
            else:
                # 决策检查点: DecisionEngine评估筛选质量
                from orchestrator.decision import DecisionEngine
                de = DecisionEngine(llm_client=self.llm, llm_model=self.model)
                top_hits = (result.screening_report.get("top_hits") or
                           result.screening_report.get("hit_list", []))[:5]
                if top_hits:
                    portfolio = de.evaluate_portfolio(top_hits, max_select=3)
                    logger.info(f"🔍 筛选质量决策: {portfolio['recommendation']}")
                    if portfolio["go_count"] == 0 and portfolio["conditional_count"] == 0:
                        logger.warning("⚠️ DecisionEngine判定筛选质量不足，但分子生成可补充")
        except Exception as e:
            err = {"stage": "virtual_screening", "error": str(e), "severity": "critical"}
            result.errors.append(err)
            logger.error(f"❌ 虚拟筛选失败: {e}")
            if config.halt_on_critical_failure:
                result.halted = True
                result.halt_reason = f"虚拟筛选异常: {e}"
                return self._finalize(result, stages, start_time)

        # ========== Stage 3: 分子生成 (关键阶段) ==========
        logger.info("📍 Stage 3: 分子生成 [CRITICAL]")
        try:
            from molecular_generation.engine import MolecularGenerationEngine
            mg = MolecularGenerationEngine()
            generation = mg.generate_candidates(
                target_name=config.target,
                n_generate=config.n_generate,
                top_n=config.top_n
            )
            result.generation_report = asdict(generation)
            stages.append("molecular_generation")

            # 检查点: 分子生成是否产生有效分子
            valid_mols = result.generation_report.get("valid_molecules", 0)
            if valid_mols == 0:
                err = {"stage": "molecular_generation", "error": "未生成有效分子", "severity": "critical"}
                result.errors.append(err)
                logger.error("❌ 分子生成未产生有效分子")
                if config.halt_on_critical_failure:
                    result.halted = True
                    result.halt_reason = "分子生成未产生有效分子"
                    return self._finalize(result, stages, start_time)
        except Exception as e:
            err = {"stage": "molecular_generation", "error": str(e), "severity": "critical"}
            result.errors.append(err)
            logger.error(f"❌ 分子生成失败: {e}")
            if config.halt_on_critical_failure:
                result.halted = True
                result.halt_reason = f"分子生成异常: {e}"
                return self._finalize(result, stages, start_time)

        # 检查点: 验证有候选分子可用
        has_candidates = (result.generation_report and
                         result.generation_report.get("top_candidates"))
        if not has_candidates:
            logger.warning("⚠️ 无候选分子可供后续阶段使用，Pipeline提前完成")
            return self._finalize(result, stages, start_time)

        # ========== Stage 4: ADMET评估 (非关键阶段) ==========
        logger.info("📍 Stage 4: ADMET评估 [NON-CRITICAL]")
        try:
            from admet_prediction.engine import ADMETEngine
            admet = ADMETEngine()

            smiles_list = [c["smiles"] for c in result.generation_report["top_candidates"][:10]]
            admet_results = admet.batch_predict(smiles_list)
            result.admet_reports = admet_results
            stages.append("admet_prediction")
        except Exception as e:
            err = {"stage": "admet_prediction", "error": str(e), "severity": "warning"}
            result.errors.append(err)
            logger.warning(f"⚠️ ADMET评估失败（非关键，继续）: {e}")

        # ========== Stage 5: 先导优化 (非关键阶段) ==========
        logger.info("📍 Stage 5: 先导优化 [NON-CRITICAL]")
        try:
            from lead_optimization.engine import LeadOptimizationEngine
            lo = LeadOptimizationEngine()

            # 优先用ADMET通过的分子，降级用generation top候选
            pass_smiles = [
                r["smiles"] for r in result.admet_reports
                if r.get("pass_filter", False) and r.get("recommendation") == "pass"
            ]

            if not pass_smiles:
                # 降级: 用generation报告中的top候选
                fallback = (result.generation_report or {}).get("top_candidates", [])[:3]
                pass_smiles = [c["smiles"] for c in fallback]
                if pass_smiles:
                    logger.info(f"ℹ️ 无ADMET通过分子，降级使用generation候选: {len(pass_smiles)}个")

            if pass_smiles:
                opt_result = lo.optimize(
                    starting_smiles=pass_smiles[0],
                    max_generations=10,
                    population_size=20
                )
                result.optimization_report = opt_result
                stages.append("lead_optimization")
                result.final_candidates = opt_result.get("top_candidates", [])[:config.top_n]
            else:
                logger.warning("⚠️ 无可优化分子，跳过先导优化")
        except Exception as e:
            err = {"stage": "lead_optimization", "error": str(e), "severity": "warning"}
            result.errors.append(err)
            logger.warning(f"⚠️ 先导优化失败（非关键，继续）: {e}")

        return self._finalize(result, stages, start_time)

    def _finalize(
        self,
        result: PipelineResult,
        stages: list[str],
        start_time: datetime
    ) -> PipelineResult:
        """完成Pipeline，记录耗时和摘要"""
        elapsed = (datetime.now() - start_time).total_seconds()
        result.stages_completed = stages
        result.execution_time = round(elapsed, 1)

        status = "🔴 已终止" if result.halted else "🟢 完成"
        error_count = len(result.errors)

        logger.info(f"""
╔══════════════════════════════════════════════╗
║  Pipeline {status:<33s} ║
║  耗时: {elapsed:.1f}s{' ' * (36 - len(f'{elapsed:.1f}s'))}║
║  完成阶段: {len(stages)}{' ' * (33 - len(str(len(stages))))}║
║  最终候选: {len(result.final_candidates)}{' ' * (33 - len(str(len(result.final_candidates))))}║
║  错误/警告: {error_count}{' ' * (32 - len(str(error_count)))}║
╚══════════════════════════════════════════════╝
        """)

        if result.halted:
            logger.error(f"🛑 Pipeline终止原因: {result.halt_reason}")

        return result
