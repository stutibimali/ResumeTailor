from pathlib import Path
from dotenv import load_dotenv
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent
VECTOR_STORE_PATH = BASE_DIR / "vector_store"

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=os.getenv("GOOGLE_API_KEY"), temperature=0)

vector_store = FAISS.load_local(str(VECTOR_STORE_PATH), embeddings, allow_dangerous_deserialization=True)

query = "Experience with Python and JavaScript, knowledge of cloud platforms like AWS or Azure, and familiarity with CI/CD pipelines for AI/ML model deployment. Strong problem-solving skills, ability to work in a collaborative environment, and excellent communication skills."

results = vector_store.similarity_search(query, k=3)

for i, document in enumerate(results, start=1):
    print("\n"+"="*60)
    print(f"Result {i}:")
    print("\n"+"="*60)
    print(document.page_content)
    print("\n SOURCE: \n")
    print(document.metadata)