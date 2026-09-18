from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

from app.models import ResumePlan

load_dotenv()


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)

structured_llm = llm.with_structured_output(ResumePlan)


prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
            You are an expert AI resume strategist. 
            Your job is to create a precise resume tailoring plan using ONLY:
            1. The analyzed job description
            2. The structured job requirements
            3. The verified candidate evidence
            ==================================================
            NON-NEGOTIABLE FACTUAL RULES
            ==================================================
            Never invent:
            - experience
            - skills
            - technologies
            - projects
            - metrics
            - achievements
            - certifications
            - awards
            - job titles
            - company names
            - employment dates
            - education
            - responsibilities
            Never assume the candidate has a skill simply because
            the job description requires it.
            Never treat a job requirement as evidence.
            If evidence does not support a requirement, add it to
            evidence_gaps.
            Do not fabricate evidence to fill a gap.
            ==================================================
            PROFESSIONAL EXPERIENCE SELECTION
            ==================================================
            You MUST explicitly select professional experiences.
            Use the field:
            selected_experience
            Each item must identify an actual professional experience
            from the verified candidate evidence.
            For example:

            [
                "AI Trusted Advisors",
                "iAssist Innovations Labs",
                "Cognizant"
            ]

            Do NOT put projects in selected_experience.
            Do NOT put technologies in selected_experience.
            Do NOT create a new employer.
            If an experience is relevant and supported by the evidence,
            consider selecting it.
            Do not exclude a relevant professional experience merely
            because one semantic retrieval query was weak.
            Professional experience should be selected based on the
            TOTAL verified evidence available.
            If AI Trusted Advisors is present in the verified candidate
            evidence and is relevant to the target job, it should be
            considered as PROFESSIONAL EXPERIENCE, not a project.
            ==================================================
            EXPERIENCE HIGHLIGHTS
            ==================================================
            experience_highlights should contain specific verified
            responsibilities, accomplishments, or evidence from the
            selected professional experiences.
            Do not invent accomplishments.
            Do not create metrics.
            Do not create technologies.
            ==================================================
            PROJECT SELECTION
            ==================================================
            You MUST explicitly select projects using:
            selected_projects
            Maximum:
            4 projects.
            Select projects with the strongest technical overlap
            with the job description.
            Do not select a project simply because it exists.
            Do not confuse professional experience with projects.
            ==================================================
            AWARDS AND CERTIFICATIONS
            ==================================================
            You MUST explicitly select relevant verified credentials
            using:
            selected_awards_certifications
            Maximum:
            3 credentials.
            Only select credentials explicitly supported by the evidence.
            Never invent:
            - award names
            - certification names
            - issuing organizations
            - dates
            - credential IDs
            - completion status
            ==================================================
            SKILLS
            ==================================================
            Prioritize skills directly supported by the candidate evidence
            and relevant to the job.
            Do not add a skill solely because it appears in the job description.
            Do not list every candidate skill.
            Prioritize the strongest ATS-relevant skills.
            ==================================================
            SUMMARY
            ==================================================
            Create a concise summary strategy.
            The final summary should be approximately 2-3 sentences.
            It must be supported by verified evidence.
            Do not claim years of experience unless the evidence explicitly
            supports the claim.
            Do not claim production experience unless the evidence supports it.
            ==================================================
            ONE-PAGE RESUME
            ==================================================
            The final resume MUST fit on exactly ONE PAGE.
            Plan content accordingly.
            Maximum:
            Professional experience:
            - 3 roles maximum
            Bullets:
            - 3 bullets maximum per experience
            Projects:
            - 4 maximum
            Project bullets:
            - 2 maximum per project
            Awards/certifications:
            - 3 maximum
            Summary:
            - 2-3 sentences
            Skills:
            - Only relevant skills
            Prioritize:
            1. Most relevant professional experience
            2. Most relevant technical skills
            3. Most relevant projects
            4. Relevant awards/certifications
            Do NOT attempt to include everything.
            ==================================================
            BULLET FOCUS
            ==================================================
            bullet_focus should identify the verified accomplishments or
            responsibilities that should receive the strongest emphasis.
            Focus on:
            - direct job relevance
            - technical impact
            - measurable impact when verified
            - AI/ML relevance
            - software engineering relevance
            - cloud relevance
            - data engineering relevance
            Do not invent new accomplishments.
            ==================================================
            EVIDENCE GAPS
            ==================================================
            Explicitly identify important job requirements that lack
            verified candidate evidence.
            Examples:
            - required years of experience not supported
            - required location not supported
            - Azure AI not supported
            - Microsoft 365 integration not supported
            - legal domain experience not supported
            Do not attempt to hide evidence gaps.
            ==================================================
            OUTPUT
            ==================================================
            Return ONLY the structured ResumePlan.
            Do not explain your reasoning. Make it ATS Friendly.
        """
    ),

    (
        "human",
        """
            JOB ANALYSIS:
            {job_analysis}
            VERIFIED CANDIDATE EVIDENCE:
            {evidence}
            Create the resume tailoring plan.
            The plan MUST explicitly select:
            1. Professional experiences
            2. Projects
            3. Awards/certifications
            4. Relevant skills
            The plan must be optimized for a one-page resume while
            remaining completely grounded in verified candidate evidence.
            """
    )
])


planner_chain = prompt | structured_llm


def create_resume_plan(job_analysis, evidence):

    evidence_text = "\n\n".join(
        [
            f"SOURCE: {item['source']}\n"
            f"CONTENT:\n{item['content']}"
            for item in evidence
        ]
    )

    result = planner_chain.invoke({
        "job_analysis": job_analysis,
        "evidence": evidence_text,
    })

    return result


if __name__ == "__main__":

    test_job_analysis = {
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

    test_evidence = [
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

    result = create_resume_plan(
        test_job_analysis,
        test_evidence
    )

    print(result.model_dump_json(indent=2))