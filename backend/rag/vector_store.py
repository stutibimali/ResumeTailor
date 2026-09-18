from pathlib import Path
from dotenv import load_dotenv
import os
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE = BASE_DIR / "knowledge_base"
VECTOR_STORE_PATH = BASE_DIR / "vector_store"

def get_document_metadata(source_path: str) -> dict:
    """
    Determine the type of knowledge-base document from its path.
    """
    path = Path(source_path)
    relative_path = path.relative_to(KNOWLEDGE_BASE)
    parts = relative_path.parts
    filename = path.stem
    metadata = {
        "source": filename,
        "file_path": str(relative_path),
    }
    if "experience" in parts:
        metadata["document_type"] = "professional_experience"

        if filename == "ai_trusted_advisors":
            metadata["organization"] = "AI Trusted Advisors"
            metadata["role"] = "AI Engineer"
        elif filename == "iassist":
            metadata["organization"] = "iAssist Innovations Labs"
        elif filename == "cognizant":
            metadata["organization"] = "Cognizant"
        elif filename == "ai_assistant":
            metadata["document_type"] = "professional_experience"
            metadata["organization"] = "AI Assistant"
    elif "projects" in parts:
        metadata["document_type"] = "project"
        metadata["project_name"] = filename.replace("_", " ").title()
    elif "resume" in parts:
        metadata["document_type"] = "master_resume"
    else:
        metadata["document_type"] = "other"
    return metadata

def load_documents():
    if not KNOWLEDGE_BASE.exists():
        raise FileNotFoundError(
            f"Knowledge base does not exist: {KNOWLEDGE_BASE}"
        )  
    loader = DirectoryLoader(str(KNOWLEDGE_BASE), glob="**/*.md", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
    documents = loader.load()
    if not documents:
        raise ValueError(
            "No Markdown documents found in the knowledge base."
        )
    for document in documents:
        source_path = document.metadata.get("source", "")
        metadata = get_document_metadata(source_path)
        document.metadata.update(metadata)
    print(f"Loaded {len(documents)} documents from knowledge base.")
    return documents

def create_vector_store():
    documents = load_documents()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)
    if not chunks:
        raise ValueError(
            "Documents were loaded but produced zero chunks."
        )
    print(f"Split documents into {len(chunks)} chunks.")

    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=GOOGLE_API_KEY, temperature=0)
    vector_store = FAISS.from_documents(chunks, embeddings)
    print("Created FAISS vector store.")
    return vector_store

if __name__ == "__main__":
    vector_store = create_vector_store()
    vector_store.save_local(str(VECTOR_STORE_PATH))
    print(f"Vector store saved locally at:{VECTOR_STORE_PATH}")
