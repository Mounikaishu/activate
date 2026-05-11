"""
Placement Reality Check — Interview mode API routes.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sessions import get_session, update_session
from graph import interview_graph

router = APIRouter(prefix="/api/interview", tags=["interview"])


class AnswerRequest(BaseModel):
    answer: str


@router.post("/{session_id}/start")
async def start_interview(session_id: str):
    """
    Start an interview session. The AI interviewer introduces itself and asks the first question.
    """
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found. Upload documents first.")

    if not session.get("analysis"):
        raise HTTPException(
            status_code=400,
            detail="Run analysis first before starting interview mode."
        )

    # Reset interview history
    update_session(session_id, interview_history=[])

    # Run interview graph with empty history (triggers start instruction)
    try:
        state = {
            "session_id": session_id,
            "resume_text": session["resume_text"],
            "jd_text": session["jd_text"],
            "history": [],
            "student_answer": "",
            "ai_response": "",
        }

        result = interview_graph.invoke(state)

        # Save history
        update_session(session_id, interview_history=result["history"])

        return {
            "session_id": session_id,
            "message": result["ai_response"],
            "question_number": 1,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interview start failed: {str(e)}")


@router.post("/{session_id}/respond")
async def respond_to_interview(session_id: str, body: AnswerRequest):
    """
    Send a student's answer. The AI evaluates the answer and asks the next question.
    """
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    history = session.get("interview_history", [])

    try:
        state = {
            "session_id": session_id,
            "resume_text": session["resume_text"],
            "jd_text": session["jd_text"],
            "history": history,
            "student_answer": body.answer,
            "ai_response": "",
        }

        result = interview_graph.invoke(state)

        # Save updated history
        update_session(session_id, interview_history=result["history"])

        # Count questions asked
        question_count = sum(1 for h in result["history"] if h.startswith("Interviewer:"))

        return {
            "session_id": session_id,
            "message": result["ai_response"],
            "question_number": question_count,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interview response failed: {str(e)}")


@router.post("/{session_id}/end")
async def end_interview(session_id: str):
    """
    End the interview and get a comprehensive performance summary.
    """
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    history = session.get("interview_history", [])

    if not history:
        raise HTTPException(status_code=400, detail="No interview to end. Start an interview first.")

    try:
        state = {
            "session_id": session_id,
            "resume_text": session["resume_text"],
            "jd_text": session["jd_text"],
            "history": history,
            "student_answer": "END_INTERVIEW",
            "ai_response": "",
        }

        result = interview_graph.invoke(state)

        # Save final history
        update_session(session_id, interview_history=result["history"])

        return {
            "session_id": session_id,
            "summary": result["ai_response"],
            "total_questions": sum(1 for h in result["history"] if h.startswith("Interviewer:")),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interview end failed: {str(e)}")
