from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from graph.workflow import graph
from app.docx_generator import generate_resume_docx

app = FastAPI(
    title="AI Resume Tailor API",
    description=(
        "Evidence-grounded AI resume tailoring using "
        "Gemini, LangChain, LangGraph, RAG and FAISS."
    ),
    version="1.0.0",
    contact={
        "name": "Stuti"
    }
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TailorResumeRequest(BaseModel):
    job_description: str = Field(
        ...,
        min_length=50,
        description="Full job description to tailor the resume against."
    )


class TailorResumeResponse(BaseModel):
    target_job_title: str
    job_analysis: dict
    tailored_resume: dict
    evaluation: dict
    evidence_gaps: list[str]
    revision_count: int

def run_resume_pipeline(job_description: str):
    initial_state = {
        "job_description": job_description,
        "revision_count": 0
    }
    result = graph.invoke(initial_state)
    return result

@app.get("/")
def root():
    return {
        "message": "AI Resume Tailor API is running",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post(
    "/tailor-resume",
    response_model=TailorResumeResponse
)
def tailor_resume(request: TailorResumeRequest):

    try:
        result = run_resume_pipeline(request.job_description)

        job_analysis = result.get(
            "job_analysis",
            {}
        )

        resume_plan = result.get(
            "resume_plan",
            {}
        )

        return {
            "target_job_title": resume_plan.get(
                "target_job_title",
                job_analysis.get(
                    "job_title",
                    "Unknown"
                )
            ),

            "job_analysis": job_analysis,

            "tailored_resume": result.get(
                "draft_resume",
                {}
            ),

            "evaluation": result.get(
                "evaluation",
                {}
            ),

            "evidence_gaps": resume_plan.get(
                "evidence_gaps",
                []
            ),

            "revision_count": result.get(
                "revision_count",
                0
            )
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )

@app.post("/tailor-resume-docx")
def tailor_resume_docx(
    request: TailorResumeRequest
):
    try:
        result = run_resume_pipeline(request.job_description)
        tailored_resume = result.get("draft_resume",{})
        if not tailored_resume:
            raise HTTPException(
                status_code=500,
                detail="Resume generation returned no resume."
            )
        file_path = generate_resume_docx(
            tailored_resume,
            candidate_name="Stuti Bimali"
        )
        return FileResponse(
            path=file_path,
            media_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            filename="Stuti_Bimali_Resume.docx"
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )