from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

from app.models import TailoredResume

load_dotenv()


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)

structured_llm = llm.with_structured_output(TailoredResume)


prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
            You are an expert technical resume writer.
            Create a one-page tailored resume using ONLY the verified
            candidate evidence provided to you. Make it ATS friendly.
            ==================================================
            NON-NEGOTIABLE FACTUAL RULES
            ==================================================
            Never invent:
            1. Experience
            2. Technologies
            3. Skills
            4. Projects
            5. Metrics
            6. Certifications
            7. Awards
            8. Dates
            9. Job titles
            10. Company names
            11. Education
            12. Responsibilities

            Never infer experience merely because a skill appears
            in the job description.
            Never claim that a planned project was completed.
            Every factual statement must be supported by the
            verified candidate evidence.
            You MAY:
            - rewrite existing information professionally
            - shorten existing information
            - reorder information
            - prioritize relevant information
            - combine closely related existing information
            - improve clarity
            - improve ATS keyword alignment
            - remove irrelevant information
            ==================================================
            FOLLOW THE RESUME PLAN
            ==================================================
            The ResumePlan is authoritative for CONTENT SELECTION.
            Use:
            selected_experience
            to determine which professional experiences to include.
            Use:
            selected_projects
            to determine which projects to include.
            Use:
            selected_awards_certifications
            to determine which awards/certifications to include.
            Do NOT substitute projects for professional experience.
            Do NOT omit a selected professional experience unless
            the supplied evidence genuinely contains no usable information
            for that experience.
            ==================================================
            PROFESSIONAL EXPERIENCE
            ==================================================
            Professional experience MUST remain under the
            Professional Experience section.
            For every selected experience:
            - use the exact verified company name
            - use the exact verified job title
            - use the exact verified employment dates
            Never modify them.
            Maximum:
            3 professional experiences.
            Maximum:
            3 bullets per experience.
            If AI Trusted Advisors is selected by the ResumePlan,
            it MUST appear under Professional Experience.
            It must NOT appear under Projects.
            ==================================================
            PROJECTS
            ==================================================
            Maximum:
            4 projects.
            Maximum:
            2 bullets per project.
            Only include projects explicitly selected by the ResumePlan.
            Do not add extra projects merely because they appear
            in the evidence.
            ==================================================
            SKILLS
            ==================================================
            Only include skills supported by the evidence.
            Prioritize skills relevant to the target job.
            Do not dump the entire candidate knowledge base into
            the skills section.
            Keep the skills section compact.
            ==================================================
            SUMMARY
            ==================================================
            Maximum:
            2-3 sentences.
            Keep it concise.
            Only use claims supported by the evidence.
            Do not claim unsupported years of experience.
            ==================================================
            AWARDS AND CERTIFICATIONS
            ==================================================
            Maximum:
            3.
            Only include credentials explicitly supported by
            the verified evidence.
            Never invent:
            - award names
            - certification names
            - issuing organizations
            - dates
            - credential IDs
            - completion status
            ==================================================
            ONE-PAGE REQUIREMENT
            ==================================================
            The final resume MUST be designed to fit on ONE PAGE.
            Maximum content:
            - Summary: 2-3 sentences
            - Experience: 3 roles
            - Experience bullets: 3 per role
            - Projects: 4
            - Project bullets: 2 per project
            - Awards/certifications: 3
            
            Prioritize relevance over completeness.
            If there is too much information:
            REMOVE LESS RELEVANT CONTENT.
            Do NOT create additional content.
            Do NOT exceed these limits.
            ==================================================
            REVISION FEEDBACK
            ==================================================
            If revision feedback is provided:
            Fix the identified issues.
            However:
            DO NOT introduce new facts.
            DO NOT invent evidence.
            DO NOT change verified company names,
            titles, dates, project names, metrics or credentials.
            ==================================================
            OUTPUT
            ==================================================
            Return only the structured TailoredResume.
        """
    ),

    (
        "human",
        """
            JOB ANALYSIS:
            {job_analysis}
            RESUME PLAN:
            {resume_plan}
            VERIFIED CANDIDATE EVIDENCE:
            {evidence}
            REVISION FEEDBACK:
            {revision_feedback}
            Write the final one-page tailored resume.
            Follow the ResumePlan selections exactly.
        """
    )
])


writer_chain = prompt | structured_llm


def write_resume(
    job_analysis,
    resume_plan,
    evidence,
    revision_feedback=None
):

    if revision_feedback is None:
        revision_feedback = []

    evidence_text = "\n\n".join(
        [
            f"SOURCE: {item['source']}\n"
            f"CONTENT:\n{item['content']}"
            for item in evidence
        ]
    )

    result = writer_chain.invoke({
        "job_analysis": job_analysis,
        "resume_plan": resume_plan,
        "evidence": evidence_text,
        "revision_feedback": revision_feedback,
    })

    return result


if __name__ == "__main__":

    job_analysis = {
        "job_title": "AI Engineer",
        "job_description": """
        Build LLM applications using LangChain and LangGraph.
        Design vector databases and retrieval-augmented generation systems.
        Create production APIs using FastAPI.
        """,
        "required_skills": [
            "Python",
            "LangChain",
            "RAG",
            "AWS",
            "FastAPI"
        ],
        "preferred_skills": [
            "LangGraph"
        ],
        "experience_level": "Mid-Level",
        "location": "Remote"
    }

    resume_plan = {
        "target_job_title": "AI Engineer",

        "summary": """
        AI/ML Engineer focused on LLM applications, RAG,
        Python and FastAPI.
        """,

        "prioritized_skills": [
            "Python",
            "FastAPI",
            "RAG",
            "LLMs",
            "AWS"
        ],

        "selected_experience": [
            "iAssist Innovations Labs",
            "AI Trusted Advisors"
        ],

        "experience_highlights": [
            "Healthcare and insurance AI systems",
            "Voice AI and agent workflow automation"
        ],

        "selected_projects": [
            "ImmigRAG-USA",
            "AI Resume Tailor"
        ],

        "selected_awards_certifications": [
            "Nepal-US Hackathon 2026 - Best Demo Award",
            "AWS Cloud Practitioner Essentials",
            "HuggingFace & Anthropic MCP"
        ],

        "evidence_gaps": [],

        "bullet_focus": [
            "RAG implementation",
            "LLM application development",
            "API development",
            "AI agent development"
        ]
    }

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
            "source": "ai_trusted_advisors.md",
            "content": """
            AI Software Engineer Intern at AI Trusted Advisors.
            Worked on Voice AI, AI agents and workflow automation.
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
            LangGraph, RAG, FAISS and FastAPI.
            """
        },

        {
            "source": "master_resume.md",
            "content": """
            Awards and Certifications:

            Nepal-US Hackathon 2026 - Best Demo Award
            AWS Cloud Practitioner Essentials
            HuggingFace & Anthropic MCP
            """
        }
    ]

    result = write_resume(
        job_analysis,
        resume_plan,
        evidence
    )

    print(result.model_dump_json(indent=2))