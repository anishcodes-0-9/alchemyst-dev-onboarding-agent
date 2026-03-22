async def run_generate(session):
    features = session["integration"].get("features", [])
    use_case = session["integration"].get("useCase")
    stack = session["integration"].get("stack")
    architecture = session["integration"].get("architecture")

    code_parts = []

    # 🔹 Base stack
    if stack == "fastapi":
        code_parts.append(
"""from fastapi import FastAPI

app = FastAPI()
"""
        )

    # 🔹 PRODUCT LAYER (based on use_case ONLY)

    # Chatbot system
    if use_case == "chatbot":
        code_parts.append(
"""# Chatbot system
def chat():
    return "Hello! I'm your chatbot."
"""
        )

    # RAG system
    elif use_case == "rag":
        code_parts.append(
"""# RAG system
context_store = []

def upload_context(data):
    context_store.append(data)

def query_context():
    return context_store
"""
        )

    # Agent system
    elif use_case == "agent":
        code_parts.append(
"""# Agent system
def run_agent(task):
    return f"Executing task: {task}"
"""
        )

    # 🔹 FEATURES (COMPOSITION LAYER)

    if "memory" in features:
        code_parts.append(
"""# Memory module
memory_store = []

def store(data):
    memory_store.append(data)
    return {"status": "stored"}

def retrieve():
    return {"data": memory_store}
"""
        )

    if "auth" in features:
        code_parts.append(
"""# Auth module
def login(username, password):
    if username == "admin" and password == "admin":
        return {"token": "secure-token"}
    return {"error": "invalid credentials"}
"""
        )

    if "embedding" in features:
        code_parts.append(
"""# Embedding module
def embed(text):
    return [ord(c) for c in text]
"""
        )

    # 🔹 FINAL BUILD
    final_code = "\n\n".join(code_parts)

    yield (
        "code",
        {
            "snippet": final_code,
            "language": "python"
        }
    )

    session["stage"] = "done"

    yield (
        "done",
        {"sessionId": session["id"]}
    )