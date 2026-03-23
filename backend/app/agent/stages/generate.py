async def run_generate(session):
    # ✅ NO-OP SHORT CIRCUIT
    if session["integration"].get("no_op"):
        yield (
            "code",
            {
                "snippet": "# No changes needed. Feature already exists.",
                "language": "text"
            }
        )

        session["stage"] = "done"

        yield (
            "done",
            {"sessionId": session["id"]}
        )
        return

    features = session["integration"].get("features", [])
    use_case = session["integration"].get("useCase")
    stack = session["integration"].get("stack")
    feature = session["integration"].get("feature")

    code_parts = []

    # 🔹 BASE
    if stack == "fastapi":
        code_parts.append(
"""from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}
"""
        )

    # 🔹 PRODUCT LAYER

    if feature == "IntelliChat":
        code_parts.append(
"""
@app.get("/chat")
def chat():
    return {"response": "Streaming chatbot using IntelliChat"}
"""
        )

    elif feature == "ContextAPI":
        code_parts.append(
"""
# Context API

context_store = []

@app.post("/context/upload")
def upload_context(data: str):
    vector = [ord(c) for c in data]
    context_store.append({"text": data, "vector": vector})
    return {"status": "uploaded"}

@app.get("/context/query")
def query_context(q: str):
    results = [
        item for item in context_store
        if q.lower() in item["text"].lower()
    ][:3]

    return {
        "query": q,
        "results": results
    }
"""
        )

    # 🔹 FALLBACK

    elif use_case == "chatbot":
        code_parts.append(
"""
@app.get("/chat")
def chat():
    return {"response": "Hello! I'm your chatbot."}
"""
        )

    elif use_case == "rag":
        code_parts.append(
"""
@app.post("/embed")
def embed(text: str):
    return {"vector": [ord(c) for c in text]}

@app.get("/search")
def search(q: str):
    return {"query": q, "results": []}
"""
        )

    # 🔹 FEATURES

    if "memory" in features:
        code_parts.append(
"""
memory_store = []

@app.post("/store")
def store(data: str):
    memory_store.append(data)
    return {"status": "stored"}

@app.get("/retrieve")
def retrieve():
    return {"data": memory_store}
"""
        )

    if "auth" in features:
        code_parts.append(
"""
@app.post("/login")
def login(username: str, password: str):
    if username == "admin" and password == "admin":
        return {"token": "secure-token"}
    return {"error": "invalid credentials"}
"""
        )

    # ✅ FIX: avoid duplicate embed when ContextAPI already exists
    if "embedding" in features and feature != "ContextAPI":
        code_parts.append(
"""
@app.post("/embed")
def embed(text: str):
    return {"vector": [ord(c) for c in text]}
"""
        )

    # 🔹 FINAL
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