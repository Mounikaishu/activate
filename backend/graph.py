"""
Placement Reality Check — LangGraph workflows for analysis and interview.
"""

from langgraph.graph import StateGraph, END
from state import AnalysisState, InterviewState
from vectorstore import retrieve_chunks
from llm import llm_call
from prompts import (
    RECRUITER_ANALYSIS_PROMPT,
    SKILL_GAP_PROMPT,
    RESUME_IMPROVEMENT_PROMPT,
    INTERVIEWER_PROMPT,
    INTERVIEW_START_INSTRUCTION,
    INTERVIEW_CONTINUE_INSTRUCTION,
    INTERVIEW_END_INSTRUCTION,
)


# ═══════════════════════════════════════════
#  ANALYSIS WORKFLOW (Resume + JD → Full Report)
# ═══════════════════════════════════════════

def context_node(state: AnalysisState) -> AnalysisState:
    """Retrieve relevant chunks from both resume and JD vectorstores."""
    query = "skills experience projects education qualifications requirements"

    resume_chunks = retrieve_chunks(state["session_id"], query, doc_type="resume", k=8)
    jd_chunks = retrieve_chunks(state["session_id"], query, doc_type="jd", k=5)

    return {
        **state,
        "resume_context": "\n\n".join(resume_chunks),
        "jd_context": "\n\n".join(jd_chunks),
    }


def analyze_node(state: AnalysisState) -> AnalysisState:
    """Run recruiter analysis — verdict + detailed breakdown."""
    prompt = RECRUITER_ANALYSIS_PROMPT.format(
        resume_text=state["resume_text"],
        jd_text=state["jd_text"],
        resume_context=state["resume_context"],
        jd_context=state["jd_context"],
    )

    result = llm_call(prompt)

    # Extract verdict from the response
    verdict = "LIKELY REJECTED"
    if "LIKELY SHORTLISTED" in result.upper():
        verdict = "LIKELY SHORTLISTED"

    return {
        **state,
        "analysis": result,
        "verdict": verdict,
    }


def skill_gap_node(state: AnalysisState) -> AnalysisState:
    """Identify skill gaps and generate learning roadmap."""
    prompt = SKILL_GAP_PROMPT.format(
        resume_text=state["resume_text"],
        jd_text=state["jd_text"],
    )

    result = llm_call(prompt)
    return {**state, "skill_gaps": result}


def improvement_node(state: AnalysisState) -> AnalysisState:
    """Generate resume improvement suggestions."""
    prompt = RESUME_IMPROVEMENT_PROMPT.format(
        resume_text=state["resume_text"],
        jd_text=state["jd_text"],
    )

    result = llm_call(prompt)
    return {**state, "improvements": result}


def build_analysis_graph():
    """Build the full analysis pipeline: context → analyze → skill_gaps → improvements."""
    graph = StateGraph(AnalysisState)

    graph.add_node("context", context_node)
    graph.add_node("analyze", analyze_node)
    graph.add_node("skill_gaps", skill_gap_node)
    graph.add_node("improvements", improvement_node)

    graph.set_entry_point("context")

    graph.add_edge("context", "analyze")
    graph.add_edge("analyze", "skill_gaps")
    graph.add_edge("skill_gaps", "improvements")
    graph.add_edge("improvements", END)

    return graph.compile()


# ═══════════════════════════════════════════
#  INTERVIEW WORKFLOW (Chat-based mock interview)
# ═══════════════════════════════════════════

def interview_context_node(state: InterviewState) -> InterviewState:
    """Pass through — context is already loaded from session."""
    return state


def interview_node(state: InterviewState) -> InterviewState:
    """Generate interviewer response based on conversation history."""
    history_text = "\n".join(state["history"]) if state["history"] else "(No conversation yet)"
    student_answer = state.get("student_answer", "")

    # Determine instruction based on conversation state
    if not state["history"] and not student_answer:
        instruction = INTERVIEW_START_INSTRUCTION
        student_answer = "(Interview is starting)"
    elif student_answer.strip().upper() == "END_INTERVIEW":
        instruction = INTERVIEW_END_INSTRUCTION
        student_answer = "(Student has requested to end the interview)"
    else:
        instruction = INTERVIEW_CONTINUE_INSTRUCTION

    prompt = INTERVIEWER_PROMPT.format(
        resume_text=state["resume_text"],
        jd_text=state["jd_text"],
        history=history_text,
        student_answer=student_answer,
        instruction=instruction,
    )

    response = llm_call(prompt)
    return {**state, "ai_response": response}


def interview_memory_node(state: InterviewState) -> InterviewState:
    """Update conversation history."""
    updated_history = list(state["history"])

    if state.get("student_answer") and state["student_answer"] != "(Interview is starting)":
        updated_history.append(f"Candidate: {state['student_answer']}")

    if state.get("ai_response"):
        updated_history.append(f"Interviewer: {state['ai_response']}")

    return {**state, "history": updated_history}


def build_interview_graph():
    """Build interview pipeline: context → interview → memory."""
    graph = StateGraph(InterviewState)

    graph.add_node("context", interview_context_node)
    graph.add_node("interview", interview_node)
    graph.add_node("memory", interview_memory_node)

    graph.set_entry_point("context")

    graph.add_edge("context", "interview")
    graph.add_edge("interview", "memory")
    graph.add_edge("memory", END)

    return graph.compile()


# Pre-compile graphs
analysis_graph = build_analysis_graph()
interview_graph = build_interview_graph()
