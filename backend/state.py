"""
Placement Reality Check — LangGraph state definitions.
"""

from typing import TypedDict


class AnalysisState(TypedDict):
    session_id: str
    resume_text: str
    jd_text: str
    resume_context: str
    jd_context: str
    verdict: str
    analysis: str
    skill_gaps: str
    improvements: str


class InterviewState(TypedDict):
    session_id: str
    resume_text: str
    jd_text: str
    history: list[str]
    student_answer: str
    ai_response: str
