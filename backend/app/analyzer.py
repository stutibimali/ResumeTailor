import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from app.models import JobAnalysis

load_dotenv()


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)


structured_llm = llm.with_structured_output(JobAnalysis)


prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
            You are an expert technical recruiter and job-description analyst.

            Analyze the provided job description and extract only information
            explicitly supported by the job description.

            Identify:

            1. Job title
            2. Full job description
            3. Requirements
            4. Required skills
            5. Preferred skills
            6. Experience level
            7. Location

            For every requirement, classify it into an appropriate category.

            Possible categories include:

            - technical_skill
            - ai_ml
            - software_engineering
            - programming
            - cloud
            - data
            - experience
            - education
            - domain
            - location
            - communication
            - other

            Examples:

            "Python" -> technical_skill

            "LangChain and LangGraph" -> ai_ml

            "3-7 years of production software development" -> experience

            "Bachelor's degree in computer science" -> education

            "AWS or Azure" -> cloud

            "Experience working with legal organizations" -> domain

            "Strong communication skills" -> communication

            "Pensacola, FL" -> location

            CRITICAL RULES:

            - Do not invent requirements.
            - Do not infer requirements that are not supported by the job description.
            - Preserve the meaning of the original requirement.
            - Mark explicitly required requirements as "required".
            - Mark explicitly preferred requirements as "preferred".
            - Do not treat every requirement as a technical skill.
            - Separate experience, education, location and domain requirements
            from technical skills.

            Return only the structured JobAnalysis.
        """
    ),
    (
        "human",
        """
            Analyze this job description:

            {job_description}
        """
    )
])


analyzer_chain = prompt | structured_llm


def analyze_job(job_description: str):

    result = analyzer_chain.invoke({
        "job_description": job_description
    })

    return result