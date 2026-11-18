from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class ApplicationDeadlines(BaseModel):
    priority_deadline: Optional[str] = Field(
        default=None,
        description="Priority or early application deadline in YYYY-MM-DD format, or null if not specified.",
    )
    final_deadline: Optional[str] = Field(
        default=None,
        description="Final application deadline in YYYY-MM-DD format, or null if not specified.",
    )


class ProgramRequirementSchema(BaseModel):
    university_name: str = Field(
        description="Official full English name of the university."
    )
    program_name: str = Field(
        description="Complete name of the graduate program (e.g., M.S. in Human-Computer Interaction)."
    )
    program_category: Literal[
        "CS", "MSSE", "MSDS", "MSBA", "HCI", "MIS", "Applied Math", "Other"
    ] = Field(
        description="Domain classification tag for the program."
    )
    is_stem_designated: Optional[bool] = Field(
        default=None,
        description="Whether the program is STEM-designated (eligible for 3-year OPT). Return null if not explicitly mentioned.",
    )
    thesis_required: Literal[
        "Course-based", "Thesis-optional", "Thesis-required", "Not Specified"
    ] = Field(
        description="Degree track structure regarding thesis requirement."
    )
    gpa_minimum: Optional[float] = Field(
        default=None,
        description="Minimum GPA requirement standardized to a 4.0 scale. Return null if not specified.",
    )
    toefl_minimum: Optional[int] = Field(
        default=None,
        description="Minimum overall TOEFL iBT score required. Return null if not specified.",
    )
    toefl_notes: Optional[str] = Field(
        default=None,
        description="Sub-score requirements (e.g., Speaking >= 22) or waiver conditions, or null if none.",
    )
    gre_policy: Literal[
        "Required", "Optional", "Waived", "Not Accepted", "Not Specified"
    ] = Field(
        description="Official GRE test score submission policy."
    )
    prerequisites: List[str] = Field(
        default_factory=list,
        description="Explicitly listed prerequisite courses or background (e.g., ['Linear Algebra', 'Data Structures']). Empty list if none.",
    )
    application_deadlines: ApplicationDeadlines = Field(
        default_factory=ApplicationDeadlines,
        description="Structured application deadlines.",
    )
    source_url: str = Field(
        description="The source URL from which these requirements were extracted."
    )
    last_updated: Optional[str] = Field(
        default=None,
        description="ISO timestamp (YYYY-MM-DD) indicating when this record was extracted.",
    )