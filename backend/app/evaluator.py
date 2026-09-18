import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from app.models import ResumeEvaluation


load_dotenv()


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)


structured_llm = llm.with_structured_output(ResumeEvaluation)


prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a strict technical resume evaluator.

Your job is to evaluate whether a generated resume is accurate,
evidence-grounded, and aligned with the provided job description.

You MUST compare the resume against the VERIFIED CANDIDATE EVIDENCE.

CRITICAL RULES:

1. Do not assume a claim is true simply because it sounds plausible.
2. Every factual resume claim must have supporting evidence.
3. Flag technologies that are not supported by the evidence.
4. Flag metrics that are not supported by the evidence.
5. Flag projects that are not supported by the evidence.
6. Flag employment dates that differ from the evidence.
7. Flag job titles that differ from the evidence.
8. Flag company names that differ from the evidence.
9. Identify important job requirements that are not adequately represented.
10. Do not penalize the resume for requirements where the candidate
    legitimately has no evidence. Instead, report them as missing
    requirements or evidence gaps.

Evaluate:

- Requirement coverage
- Evidence grounding
- Unsupported claims
- Missing requirements
- Consistency
- Overall quality

The evaluator must be conservative.

If you are uncertain whether a claim is supported,
flag it for review rather than assuming it is true.

Set should_revise to true if there are unsupported claims,
important missing requirements, or meaningful consistency problems.

Return only the structured evaluation.
"""
    ),
    (
        "human",
        """
JOB ANALYSIS:

{job_analysis}


GENERATED RESUME:

{resume}


VERIFIED CANDIDATE EVIDENCE:

{evidence}


Evaluate the generated resume.
"""
    )
])


evaluator_chain = prompt | structured_llm


def evaluate_resume(job_analysis, resume, evidence):

    evidence_text = "\n\n".join(
        [
            f"SOURCE: {item['source']}\n"
            f"CONTENT:\n{item['content']}"
            for item in evidence
        ]
    )

    result = evaluator_chain.invoke({
        "job_analysis": job_analysis,
        "resume": resume,
        "evidence": evidence_text,
    })

    return result

if __name__ == "__main__":

    from app.models import JobAnalysis


    job_analysis = JobAnalysis(
        job_title="AI Engineer",

        job_description="""
        Build LLM applications using LangChain and LangGraph.
        Design vector databases and retrieval-augmented generation systems.
        Create production APIs using FastAPI.
        """,

        required_skills=[
            "Python",
            "LangChain",
            "RAG",
            "AWS",
            "FastAPI"
        ],

        preferred_skills=[
            "LangGraph"
        ],

        experience_level="Mid-Level",

        location="Remote"
    )


    resume = """
    AI Engineer

    Summary:
    AI Engineer with experience building LLM applications,
    RAG systems and production APIs using Python and FastAPI.

    Skills:
    Python, FastAPI, RAG, LangChain, AWS

    Experience:

    iAssist Innovations Labs
    AI Scientist / AI Intern
    June 2023 - July 2024

    - Developed healthcare AI automation using Python.
    - Worked on hospital bill claim analysis and automation.

    Projects:

    ImmigRAG-USA
    - Built a RAG system using hybrid BM25 and FAISS retrieval.
    - Developed a FastAPI backend for LLM-based question answering.

    AI Resume Tailor
    - Building an AI Resume Tailor using Gemini, LangChain,
      LangGraph, RAG, FAISS and FastAPI.
    """


    evidence = [
        {
            "source": "iassist.md",
            "content": """
AI Scientist / AI Intern at iAssist Innovations Labs.

Worked on healthcare and insurance-related AI systems,
including hospital bill claim analysis and automation.

Used Python and Excel for data extraction and analysis.
"""
        },

        {
            "source": "immigration_rag.md",
            "content": """
Built ImmigRAG-USA using hybrid BM25 and FAISS retrieval,
FastAPI and LLM-based question answering.
"""
        },

        {
            "source": "ai_resume_tailor.md",
            "content": """
Building an AI Resume Tailor using Gemini, LangChain,
LangGraph, RAG, FAISS, Gemini embeddings and FastAPI.
"""
        }
    ]


    result = evaluate_resume(
        job_analysis.model_dump_json(indent=2),
        resume,
        evidence
    )


    print("\n" + "=" * 70)
    print("RESUME EVALUATION")
    print("=" * 70)

    print(result.model_dump_json(indent=2))