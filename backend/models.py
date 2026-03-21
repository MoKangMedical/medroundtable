from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime

class AgentRole(str, Enum):
    # 核心临床团队 (5个)
    CLINICAL_DIRECTOR = "clinical_director"
    PHD_STUDENT = "phd_student"
    EPIDEMIOLOGIST = "epidemiologist"
    STATISTICIAN = "statistician"
    RESEARCH_NURSE = "research_nurse"
    
    # 生物信息学套件 (4个)
    PHARMACOGENOMICS_EXPERT = "pharmacogenomics_expert"
    GWAS_EXPERT = "gwas_expert"
    SINGLE_CELL_ANALYST = "single_cell_analyst"
    GALAXY_BRIDGE = "galaxy_bridge"
    
    # 专业研究Agent (5个)
    UX_RESEARCHER = "ux_researcher"
    DATA_ENGINEER = "data_engineer"
    TREND_RESEARCHER = "trend_researcher"
    EXPERIMENT_TRACKER = "experiment_tracker"
    QA_EXPERT = "qa_expert"

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
    from_role: Union[AgentRole, str]  # AgentRole or 'user'
    to_role: Union[AgentRole, str]  # 'all' for broadcast
    type: MessageType
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

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
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class RoundTable(BaseModel):
    id: str
    title: str
    clinical_question: str
    status: RoundTableStatus = RoundTableStatus.INIT
    participants: List[AgentRole] = Field(default_factory=list)
    messages: List[A2AMessage] = Field(default_factory=list)
    preferred_expert: Optional[str] = None
    human_participants: List[Dict[str, Any]] = Field(default_factory=list)
    secondme_shades: List[Dict[str, Any]] = Field(default_factory=list)
    ai_pack: Optional[Dict[str, Any]] = None
    collaboration_label: Optional[str] = None
    auto_discussion: bool = False
    human_can_interrupt: bool = True
    current_round: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    output: Optional[ResearchOutput] = None
