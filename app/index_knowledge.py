from app.services.rag import build_policy_vector_store


if __name__ == "__main__":
    print("Building policy vector store...")

    vector_store = build_policy_vector_store()

    print("Policy vector store created successfully.")