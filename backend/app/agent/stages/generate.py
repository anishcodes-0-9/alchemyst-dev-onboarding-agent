async def run_generate(session):
    features = session["integration"].get("features", [])
    use_case = session["integration"].get("useCase")
    stack = session["integration"].get("stack")
    architecture = session["integration"].get("architecture")

    code_parts = []

    if stack == "fastapi":
       code_parts.append(
"""from fastapi import FastAPI

app = FastAPI()
"""
)

    # 🔹 Chatbot base
    if use_case == "chatbot":
        code_parts.append(
            """def chat():
    return "Hello! I'm your chatbot."
"""
        )

    # 🔹 Memory
    if "memory" in features:
        code_parts.append(
            """memory_store = []

def store(data):
    memory_store.append(data)
    return {"status": "stored"}

def retrieve():
    return {"data": memory_store}
"""
        )

    # 🔹 Auth
    if "auth" in features:
        code_parts.append(
            """def login(username, password):
    if username == "admin" and password == "admin":
        return {"token": "secure-token"}
    return {"error": "invalid credentials"}
"""
        )

    # 🔹 Embeddings
    if "embedding" in features:
        code_parts.append(
            """def embed(text):
    return [ord(c) for c in text]
"""
        )

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