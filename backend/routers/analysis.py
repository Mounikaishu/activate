"""
Placement Reality Check — Analysis & Upload API routes.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from parsers import parse_document
from chunker import chunk_text
from vectorstore import store_chunks, clear_session
from sessions import create_session, get_session, update_session
from graph import analysis_graph

router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/upload")
async def upload_documents(
    resume: UploadFile = File(...),
    jd_text: str = Form(None),
    jd_file: UploadFile = File(None),
):
    """
    Upload resume + job description. Returns a session_id for analysis.
    JD can be provided as text (jd_text) or as a file upload (jd_file).
    """
    # --- Parse Resume ---
    try:
        resume_bytes = await resume.read()
        resume_text = parse_document(resume_bytes, resume.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse resume: {str(e)}")

    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume appears to be empty. Please upload a valid document.")

    # --- Parse Job Description ---
    jd_content = ""
    if jd_text and jd_text.strip():
        jd_content = jd_text.strip()
    elif jd_file:
        try:
            jd_bytes = await jd_file.read()
            jd_content = parse_document(jd_bytes, jd_file.filename)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse JD file: {str(e)}")

    if not jd_content.strip():
        raise HTTPException(status_code=400, detail="Job description is required. Paste text or upload a file.")

    # --- Create Session ---
    session_id = create_session(resume_text, jd_content)

    # --- Chunk & Store in ChromaDB ---
    resume_chunks = chunk_text(resume_text)
    jd_chunks = chunk_text(jd_content)

    store_chunks(session_id, resume_chunks, doc_type="resume")
    store_chunks(session_id, jd_chunks, doc_type="jd")

    return {
        "session_id": session_id,
        "resume_length": len(resume_text),
        "jd_length": len(jd_content),
        "resume_chunks": len(resume_chunks),
        "jd_chunks": len(jd_chunks),
        "message": "Documents uploaded successfully. Ready for analysis.",
    }


@router.get("/analyze/{session_id}")
async def run_analysis(session_id: str):
    """
    Run the full analysis pipeline: Recruiter verdict → Skill gaps → Resume improvements.
    This may take 30-60 seconds as it makes multiple LLM calls.
    """
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found. Please upload documents first.")

    # Check if analysis already exists
    if session.get("analysis") and session.get("skill_gaps") and session.get("improvements"):
        return {
            "session_id": session_id,
            "verdict": session["verdict"],
            "analysis": session["analysis"],
            "skill_gaps": session["skill_gaps"],
            "improvements": session["improvements"],
            "cached": True,
        }

    # Run LangGraph analysis pipeline
    try:
        initial_state = {
            "session_id": session_id,
            "resume_text": session["resume_text"],
            "jd_text": session["jd_text"],
            "resume_context": "",
            "jd_context": "",
            "verdict": "",
            "analysis": "",
            "skill_gaps": "",
            "improvements": "",
        }

        result = analysis_graph.invoke(initial_state)

        # Store results in session
        update_session(
            session_id,
            verdict=result["verdict"],
            analysis=result["analysis"],
            skill_gaps=result["skill_gaps"],
            improvements=result["improvements"],
        )

        return {
            "session_id": session_id,
            "verdict": result["verdict"],
            "analysis": result["analysis"],
            "skill_gaps": result["skill_gaps"],
            "improvements": result["improvements"],
            "cached": False,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/analyze/{session_id}/section/{section}")
async def get_section(session_id: str, section: str):
    """Get a specific analysis section. Valid sections: verdict, analysis, skill_gaps, improvements."""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    valid_sections = ["verdict", "analysis", "skill_gaps", "improvements"]
    if section not in valid_sections:
        raise HTTPException(status_code=400, detail=f"Invalid section. Use: {valid_sections}")

    value = session.get(section)
    if not value:
        raise HTTPException(status_code=404, detail=f"Section '{section}' not yet generated. Run /analyze first.")

    return {"session_id": session_id, "section": section, "content": value}


@router.delete("/session/{session_id}")
async def delete_session_endpoint(session_id: str):
    """Delete a session and its vectorstore data."""
    clear_session(session_id)
    from sessions import delete_session
    delete_session(session_id)
    return {"message": "Session deleted."}
