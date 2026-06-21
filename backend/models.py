from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class AgentRole(str, Enum):
    CLINICAL_DIRECTOR = "clinical_director"
    PHD_STUDENT = "phd_student"
    EPIDEMIOLOGIST = "epidemiologist"
    STATISTICIAN = "statistician"
    RESEARCH_NURSE = "research_nurse"

class MessageType(str, Enum):
    PROPOSAL = "proposal"
    QUESTION = "question"
    FEEDBACK = "feedback"
    AGREEMENT = "agreement"
    OBJECTION = "objection"
    SUMMARY = "summary"
    INTRODUCTION = "introduction"

class RoundTableStatus(str, Enum):
    INIT = "init"
    PROBLEM_PRESENTATION = "problem_presentation"
    DISCUSSION_ROUND_1 = "discussion_round_1"
    SCENARIO_DESIGN = "scenario_design"
    CRF_DESIGN = "crf_design"
    EXECUTION_PLAN = "execution_plan"
    CONSENSUS_REACHED = "consensus_reached"
    OUTPUT_GENERATION = "output_generation"
    COMPLETED = "completed"

class A2AMessage(BaseModel):
    id: str
    session_id: str
    from_role: AgentRole | str  # AgentRole or 'user'
    to_role: AgentRole | str  # 'all' for broadcast
    type: MessageType
    content: str
    metadata: Dict[str, Any] = {}
    created_at: datetime = datetime.utcnow()

class StudyDesign(BaseModel):
    study_type: str
    title: str
    background: str
    objectives: List[str]
    inclusion_criteria: List[str]
    exclusion_criteria: List[str]
    sample_size: int
    study_duration: str
    primary_endpoint: str
    secondary_endpoints: List[str]
    statistical_methods: List[str]
    quality_control: List[str]

class CRFTemplate(BaseModel):
    sections: List[Dict[str, Any]]
    variables: List[Dict[str, Any]]
    validation_rules: List[str]

class AnalysisPlan(BaseModel):
    descriptive_stats: str
    primary_analysis: str
    secondary_analyses: List[str]
    subgroup_analyses: List[str]
    sensitivity_analyses: List[str]
    missing_data_handling: str

class ResearchOutput(BaseModel):
    study_design: StudyDesign
    crf_template: CRFTemplate
    analysis_plan: AnalysisPlan
    operation_manual: str
    generated_at: datetime = datetime.utcnow()

class RoundTable(BaseModel):
    id: str
    title: str
    clinical_question: str
    status: RoundTableStatus = RoundTableStatus.INIT
    participants: List[AgentRole] = []
    messages: List[A2AMessage] = []
    current_round: int = 0
    created_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None
    output: Optional[ResearchOutput] = None
