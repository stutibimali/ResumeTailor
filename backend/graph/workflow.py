from typing import TypedDict, List, Dict, Any

from langgraph.graph import StateGraph, START, END

from app.analyzer import analyze_job
from rag.evidence import retrieve_evidence
from app.planner import create_resume_plan
from app.writer import write_resume
from app.evaluator import evaluate_resume


class ResumeState(TypedDict, total=False):
    job_description: str
    job_analysis: Dict[str, Any]
    evidence: List[Dict[str, Any]]
    resume_plan: Dict[str, Any]
    draft_resume: Dict[str, Any]
    evaluation: Dict[str, Any]
    revision_feedback: List[str]
    revision_count: int
    
# ---------------------------------------------------------
# NODE 1: Analyze Job
# ---------------------------------------------------------

def analyze_job_node(state: ResumeState):
    result = analyze_job(
        state["job_description"]
    )
    return {
        "job_analysis": result.model_dump()
    }

# ---------------------------------------------------------
# NODE 2: Retrieve Evidence
# ---------------------------------------------------------

def retrieve_evidence_node(state: ResumeState):
    job_analysis = state["job_analysis"]
    evidence = retrieve_evidence(
        job_analysis
    )
    return {
        "evidence": evidence
    }

# ---------------------------------------------------------
# NODE 3: Create Resume Plan
# ---------------------------------------------------------

def create_plan_node(state: ResumeState):
    plan = create_resume_plan(
        state["job_analysis"],
        state["evidence"]
    )
    return {
        "resume_plan": plan.model_dump()
    }

# ---------------------------------------------------------
# NODE 4: Write Resume
# ---------------------------------------------------------

def write_resume_node(state: ResumeState):
    resume = write_resume(
        state["job_analysis"],
        state["resume_plan"],
        state["evidence"],
        state.get("revision_feedback", []),
    )
    return {
        "draft_resume": resume.model_dump()
    }

# ---------------------------------------------------------
# NODE 5: Evaluate Resume
# ---------------------------------------------------------

def evaluate_resume_node(state):
    evaluation = evaluate_resume(
        state["job_analysis"],
        state["draft_resume"],
        state["evidence"]
    )
    evaluation_dict = evaluation.model_dump()
    feedback = []
    feedback.extend(
        evaluation_dict.get(
            "unsupported_claims",
            []
        )
    )
    feedback.extend(
        evaluation_dict.get(
            "missing_requirements",
            []
        )
    )
    feedback.extend(
        evaluation_dict.get(
            "consistency_issues",
            []
        )
    )
    feedback.extend(
        evaluation_dict.get(
            "improvement_suggestions",
            []
        )
    )
    return {
        "evaluation": evaluation_dict,
        "revision_feedback": feedback,
    }


# ---------------------------------------------------------
# NODE 6: Decide Whether to Revise
# ---------------------------------------------------------

def should_revise(state: ResumeState):
    evaluation = state["evaluation"]
    revision_count = state.get(
        "revision_count",
        0
    )
    if evaluation["should_revise"] and revision_count < 2:
        return "revise"
    return "finish"


# ---------------------------------------------------------
# NODE 7: Revision Counter
# ---------------------------------------------------------

def increment_revision(state: ResumeState):
    return {
        "revision_count": state.get(
            "revision_count",
            0
        ) + 1
    }


# ---------------------------------------------------------
# BUILD GRAPH
# ---------------------------------------------------------

graph_builder = StateGraph(ResumeState)

graph_builder.add_node(
    "analyze_job",
    analyze_job_node
)

graph_builder.add_node(
    "retrieve_evidence",
    retrieve_evidence_node
)

graph_builder.add_node(
    "create_plan",
    create_plan_node
)

graph_builder.add_node(
    "write_resume",
    write_resume_node
)

graph_builder.add_node(
    "evaluate_resume",
    evaluate_resume_node
)

graph_builder.add_node(
    "increment_revision",
    increment_revision
)

# ---------------------------------------------------------
# EDGES
# ---------------------------------------------------------

graph_builder.add_edge(
    START,
    "analyze_job"
)

graph_builder.add_edge(
    "analyze_job",
    "retrieve_evidence"
)

graph_builder.add_edge(
    "retrieve_evidence",
    "create_plan"
)

graph_builder.add_edge(
    "create_plan",
    "write_resume"
)

graph_builder.add_edge(
    "write_resume",
    "evaluate_resume"
)


graph_builder.add_conditional_edges(
    "evaluate_resume",
    should_revise,
    {
        "revise": "increment_revision",
        "finish": END
    }
)


graph_builder.add_edge(
    "increment_revision",
    "write_resume"
)

graph = graph_builder.compile()

if __name__ == "__main__":

    job_description = """
    We are looking for an AI Engineer with experience in Python,
    LangChain, RAG, AWS and FastAPI.

    The engineer will build LLM applications, develop AI agents,
    design retrieval systems and create production APIs.

    Experience with LangGraph is preferred.
    """

    initial_state = {
        "job_description": job_description,
        "revision_count": 0
    }

    result = graph.invoke(
        initial_state
    )

    print("\n")
    print("=" * 80)
    print("FINAL RESUME")
    print("=" * 80)

    print(
        result["draft_resume"]
    )

    print("\n")
    print("=" * 80)
    print("EVALUATION")
    print("=" * 80)

    print(
        result["evaluation"]
    )

    print("\n")
    print(
        "Revisions:",
        result.get("revision_count", 0)
    )