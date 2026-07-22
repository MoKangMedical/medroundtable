from backend.reliability_collaboration import (
    ExpertOpinion,
    ReliabilityAssessmentRequest,
    assess_reliability,
)


def opinion(agent_id, conclusion, confidence, evidence=None, uncertainties=None):
    return ExpertOpinion(
        agent_id=agent_id,
        specialty=agent_id,
        conclusion=conclusion,
        confidence=confidence,
        evidence_items=evidence or [],
        uncertainties=uncertainties or [],
    )


def assess(opinions):
    return assess_reliability(
        ReliabilityAssessmentRequest(
            case_id="test-case",
            question="Which analysis should be used?",
            opinions=opinions,
        )
    )


def test_easy_consensus_can_pass_signing_gate():
    result = assess(
        [
            opinion("clinical", "Use Cox model", 0.82, ["protocol", "cohort"], ["PH assumption"]),
            opinion("statistics", "Use Cox model", 0.78, ["DAG", "simulation"], ["calibration"]),
            opinion("data", "Use Cox model", 0.80, ["dictionary", "missingness"], ["coding"]),
        ]
    )
    assert result["reliability_tier"]["code"] == "easy"
    assert result["policy"]["signing_allowed"] is True


def test_mixed_opinions_require_adjudication():
    result = assess(
        [
            opinion("clinical", "Use Cox model", 0.82, ["protocol", "cohort"], ["PH assumption"]),
            opinion("statistics", "Use Cox model", 0.76, ["DAG", "simulation"], ["calibration"]),
            opinion("data", "Use XGBoost", 0.71, ["benchmark"], ["interpretability"]),
        ]
    )
    assert result["reliability_tier"]["code"] == "medium"
    assert result["policy"]["route"] == "adjudicate_disagreement"
    assert result["policy"]["signing_allowed"] is False


def test_unanimous_low_evidence_is_not_treated_as_easy():
    result = assess(
        [
            opinion("clinical", "Use XGBoost", 0.91),
            opinion("statistics", "Use XGBoost", 0.88),
            opinion("data", "Use XGBoost", 0.90),
        ]
    )
    assert result["reliability_tier"]["code"] == "hard"
    assert any(flag["code"] == "consensus_without_evidence" for flag in result["risk_flags"])
    assert result["policy"]["signing_allowed"] is False


def test_stronger_minority_evidence_triggers_independent_review():
    result = assess(
        [
            opinion("clinical", "Use score A", 0.70, ["opinion"]),
            opinion("statistics", "Use score A", 0.68, ["opinion"]),
            opinion("auditor", "Use score B", 0.89, ["external validation", "code audit", "replication"]),
        ]
    )
    assert result["reliability_tier"]["code"] == "hard"
    assert any(flag["code"] == "minority_with_stronger_evidence" for flag in result["risk_flags"])
