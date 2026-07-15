"""
Placement Reality Check — FastAPI Application Entry Point.
A brutally honest AI-powered resume analysis platform.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.analysis import router as analysis_router
from routers.interview import router as interview_router

app = FastAPI(
    title="Placement Reality",
    description="Brutally honest AI-powered resume analysis against specific job descriptions",
    version="1.0.0",
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(analysis_router)
app.include_router(interview_router)


@app.get("/")
async def root():
    """Health check / API info."""
    return {
        "status": "ok",
        "app": "Placement Reality Check",
        "version": "1.0.0",
        "description": "Upload Resume + JD → Get brutally honest recruiter analysis",
        "endpoints": {
            "upload": "POST /api/upload — Upload resume (PDF/DOCX) + job description",
            "analyze": "GET /api/analyze/{session_id} — Run full analysis pipeline",
            "section": "GET /api/analyze/{session_id}/section/{section} — Get specific section",
            "interview_start": "POST /api/interview/{session_id}/start — Start mock interview",
            "interview_respond": "POST /api/interview/{session_id}/respond — Answer a question",
            "interview_end": "POST /api/interview/{session_id}/end — End interview + get summary",
        },
        "docs": "/docs",
    }
