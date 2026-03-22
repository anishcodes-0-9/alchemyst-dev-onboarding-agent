async def run_generate(session):
    feature = session["integration"].get("feature")

    if feature == "IntelliChat":
        code = """from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def chat():
    return {"response": "Hello! I'm your chatbot."}
"""

    elif feature == "ContextAPI":
        code = """from fastapi import FastAPI

app = FastAPI()

memory_store = []

@app.post("/store")
def store(data: str):
    memory_store.append(data)
    return {"status": "stored"}

@app.get("/retrieve")
def retrieve():
    return {"data": memory_store}
"""

    elif feature == "ContextRouter":
        code = """def route(query):
    if "code" in query:
        return "Code Model"
    return "General Model"
"""

    else:
        code = "# No suitable integration found"

    yield (
        "code",
        {
            "snippet": code,
            "language": "python"
        }
    )

    session["stage"] = "done"

    yield (
        "done",
        {"sessionId": session["id"]}
    )