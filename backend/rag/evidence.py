from rag.retriever import get_retriever


def retrieve_evidence(job_analysis):
    """
    Retrieve evidence from the candidate knowledge base
    for each job requirement.

    Evidence retains metadata identifying whether it came from
    professional experience, a project, the master resume, etc.
    """
    retriever = get_retriever()
    requirements = job_analysis.get("requirements",[])

    evidence = []
    seen = set()

    def add_documents(
        documents,
        requirement,
        category,
        priority
    ):
        for document in documents:
            source = document.metadata.get(
                "source",
                "unknown"
            )
            content = document.page_content.strip()
            if not content:
                continue
            metadata = document.metadata
            document_type = metadata.get("document_type","unknown")
            source = metadata.get("source","unknown")
            organization = metadata.get("organization")
            role = metadata.get("role")
            project_name = metadata.get("project_name")
            key = (
                requirement,
                source,
                content
            )
            if key in seen:
                continue
            seen.add(key)
            evidence_item ={
                "requirement": requirement,
                "category": category,
                "priority": priority,
                "document_type": document_type,
                "source": source,
                "content": content
            }
            if organization:
                evidence_item["organization"] = organization
            if role:
                evidence_item["role"] = role
            if project_name:
                evidence_item["project_name"] = project_name
            evidence.append(evidence_item)
                            
    for item in requirements:
        requirement = item.get("requirement","")
        category = item.get("category","other")
        priority = item.get("priority","required")
        
        if not requirement:
            continue
        
        if category == "location":
            continue
        
        documents = retriever.invoke(requirement)

        add_documents(
            documents,
            requirement,
            category,
            priority
        )
        
    job_title = job_analysis.get(
        "job_title",
        ""
    )

    broad_query = f"""
    Candidate experience relevant to:
    {job_title}

    AI engineering
    machine learning
    generative AI
    LLM applications
    AI agents
    agentic workflows
    RAG
    Python
    APIs
    cloud
    AWS
    software engineering
    workflow automation
    data processing
    """

    broad_documents = retriever.invoke(
        broad_query
    )

    add_documents(
        broad_documents,
        "candidate-wide experience",
        "candidate_experience",
        "context"
    )

    return evidence