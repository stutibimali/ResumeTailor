from pydantic import BaseModel, Field
from typing import List

class Requirement(BaseModel):
    category: str = Field(
        description=(
            "Requirement category such as technical_skill, "
            "ai_ml, experience, education, cloud, "
            "software_engineering, domain, location, or other."
        )
    )
    requirement: str = Field(
        description="The specific requirement from the job description."
    )
    priority: str = Field(
        description="required or preferred."
    )

class JobAnalysis(BaseModel):
    job_title: str
    job_description: str
    requirements: List[Requirement]
    required_skills: List[str]
    preferred_skills: List[str]
    experience_level: str
    location: str

class EvidenceItem(BaseModel):
    content: str = Field(..., description="The content of the evidence item")
    source: str = Field(..., description="The source of the evidence item")
    relevance_score: float | None = Field(None, description="The relevance score of the evidence item")

class ResumePlan(BaseModel):
    target_job_title: str = Field(..., description="The target job title for the resume")
    summary: str = Field(..., description="A summary of the resume plan")
    prioritized_skills: List[str] = Field(..., description="List of prioritized skills for the resume")
    selected_experience: List[str]
    experience_highlights: List[str] = Field(..., description="List of experience highlights for the resume")
    selected_projects: List[str] = Field(..., description="List of selected projects for the resume")
    selected_awards_certifications: List[str] = Field(..., description="List of selected certification and award")
    evidence_gaps: List[str] = Field(..., description="List of evidence gaps identified in the resume plan")
    bullet_focus: List[str] = Field(..., description="List of bullet points to focus on in the resume")

class ResumeExperience(BaseModel):
    company: str
    title: str
    dates: str
    bullets: List[str]

class ResumeProject(BaseModel):
    name: str
    bullets: List[str]

class ResumeCertification(BaseModel):
    name:str
    
class TailoredResume(BaseModel):
    target_title: str
    summary: str
    targeted_skills: List[str]
    experience: List[ResumeExperience]
    projects: List[ResumeProject]
    awards_certifications: List[ResumeCertification] = []

class RequirementEvaluation(BaseModel):
    requirement: str
    status: str
    evidence: str

class ResumeEvaluation(BaseModel):
    overall_assessment: str
    requirement_coverage: List[RequirementEvaluation]
    unsupported_claims: List[str]
    missing_requirements: List[str]
    consistency_issues: List[str]
    improvement_suggestions: List[str]
    should_revise: bool