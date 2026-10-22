from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class ExtractedClaimData(BaseModel):
    patient_age: Optional[int] = Field(default=None, description="Age of the patient")
    patient_gender: Optional[str] = Field(default=None, description="Gender (Male/Female/Other)")
    diagnosis_code: Optional[str] = Field(default=None, description="ICD-10 diagnosis code")
    diagnosis_description: Optional[str] = Field(default=None, description="Description of diagnosis")
    procedure_code: Optional[str] = Field(default=None, description="Procedure or treatment code")
    procedure_description: Optional[str] = Field(default=None, description="Description of procedure")
    admission_date: Optional[str] = Field(default=None, description="Admission date in YYYY-MM-DD")
    estimated_cost: Optional[float] = Field(default=None, description="Estimated total hospital charges")
    hospital_name: Optional[str] = Field(default=None, description="Name of the hospital")
    policy_number: Optional[str] = Field(default=None, description="Insurance policy identifier")
    submitted_documents: List[str] = Field(default_factory=list, description="List of recognized document types")

class DecisionVerdict(BaseModel):
    verdict: Literal["Approve", "Query", "Reject"] = Field(description="Adjudication recommendation")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    rationale: str = Field(description="Explainable clinical and policy rationale")
    citations: List[str] = Field(default_factory=list, description="Citations to policy clauses and rules")
    unresolved_issues: List[str] = Field(default_factory=list, description="Issues requiring review or documents")