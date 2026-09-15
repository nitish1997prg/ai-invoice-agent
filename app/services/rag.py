from pathlib import Path

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config.settings import get_settings

settings = get_settings()
policy_path = settings.policy_path
vector_store_path = settings.chroma_db_path
collection_name = settings.collection_name


def get_embeddings():
    return OllamaEmbeddings(
        model=settings.ollama_embedding_model,
    )


def build_policy_vector_store():
            
    if not policy_path.exists():
        raise FileNotFoundError(
            f"Policy file not found: {policy_path}"
        )

    policy_text = policy_path.read_text(encoding="utf-8")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
    )

    documents = text_splitter.create_documents(
        texts=[policy_text],
        metadatas=[
            {
                "source": "invoice_policy.txt",
                "document_type": "company_policy",
            }
        ],
    )

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=get_embeddings(),
        persist_directory=str(vector_store_path),
        collection_name=collection_name,
    )

    return vector_store


def get_policy_vector_store():
    if not vector_store_path.exists():
        raise FileNotFoundError(
            "Policy vector store does not exist. "
            "Run: uv run python -m app.index_knowledge"
        )

    return Chroma(
        collection_name=collection_name,
        persist_directory=str(vector_store_path),
        embedding_function=get_embeddings(),
    )


def get_policy_retriever():
    vector_store = ensure_policy_vector_store()

    return vector_store.as_retriever(
        search_kwargs={"k": 3}
    )

def ensure_policy_vector_store():
    try:
        vector_store = get_policy_vector_store()

        # Verify that the collection contains documents.
        collection_data = vector_store.get()

        if collection_data.get("ids"):
            return vector_store

    except Exception:
        pass

    return build_policy_vector_store()


def retrieve_policy(query: str) -> str:
    retriever = get_policy_retriever()
    documents = retriever.invoke(query)

    if not documents:
        return "No relevant policy information was found."

    return "\n\n".join(
        document.page_content
        for document in documents
    )