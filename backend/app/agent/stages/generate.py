from __future__ import annotations
from app.models.session import SessionState


async def run_generate(session: SessionState, requested_language: str | None = None):
    # fallback for loop.py calls
    if requested_language is None:
        requested_language = session.integration.language

    # no_op: only skip if same language
    if (
        session.integration.no_op and
        session.integration.language == requested_language
    ):
        yield (
            "code",
            {
                "snippet": "# No changes needed. Feature already exists.",
                "language": session.integration.language
            }
        )
        yield ("token", {"text": "You already have a working integration set up. Want me to help you deploy it or extend it with additional features?"})
        session.stage = "done"
        yield ("done", {"sessionId": session.id})
        return

    # update language before generation
    session.integration.language = requested_language

    features = session.integration.features
    use_case = session.integration.useCase
    stack = session.integration.stack
    feature = session.integration.feature
    language = session.integration.language

    code_parts = []

    if language == "python":
        # BASE
        if stack == "fastapi":
            code_parts.append(
"""from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}
""")

        if feature == "IntelliChat":
            code_parts.append(
"""
@app.get("/chat")
def chat():
    return {"response": "Streaming chatbot using IntelliChat"}
""")

        elif feature == "ContextAPI":
            code_parts.append(
"""
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
    return {"query": q, "results": results}
""")

        elif feature == "ContextRouter":
            code_parts.append(
"""
from openai import AsyncOpenAI

client = AsyncOpenAI(
    base_url="https://api.getalchemystai.com/v1",
    api_key="YOUR_ALCHEMYST_API_KEY"
)

@app.post("/chat")
async def chat(message: str):
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": message}]
    )
    return {"response": response.choices[0].message.content}
""")

        elif use_case == "chatbot":
            code_parts.append(
"""
@app.get("/chat")
def chat():
    return {"response": "Hello! I'm your chatbot."}
""")

        elif use_case == "rag":
            code_parts.append(
"""
@app.post("/embed")
def embed(text: str):
    return {"vector": [ord(c) for c in text]}

@app.get("/search")
def search(q: str):
    return {"query": q, "results": []}
""")

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
""")

        if "auth" in features:
            code_parts.append(
"""
@app.post("/login")
def login(username: str, password: str):
    if username == "admin" and password == "admin":
        return {"token": "secure-token"}
    return {"error": "invalid credentials"}
""")

        if "embedding" in features and feature != "ContextAPI":
            code_parts.append(
"""
@app.post("/embed")
def embed(text: str):
    return {"vector": [ord(c) for c in text]}
""")

    elif language == "javascript":
        if feature == "IntelliChat":
            code_parts.append(
"""const express = require('express');
const app = express();
app.use(express.json());

app.get('/chat', (req, res) => {
  res.json({ response: 'Streaming chatbot using IntelliChat' });
});

app.listen(3000, () => console.log('Server running on port 3000'));
""")

        elif feature == "ContextAPI":
            code_parts.append(
"""const express = require('express');
const app = express();
app.use(express.json());

const contextStore = [];

app.post('/context/upload', (req, res) => {
  const { data } = req.body;
  contextStore.push({ text: data });
  res.json({ status: 'uploaded' });
});

app.get('/context/query', (req, res) => {
  const { q } = req.query;
  const results = contextStore
    .filter(item => item.text.toLowerCase().includes(q.toLowerCase()))
    .slice(0, 3);
  res.json({ query: q, results });
});

app.listen(3000, () => console.log('Server running on port 3000'));
""")

        elif feature == "ContextRouter":
            code_parts.append(
"""const OpenAI = require('openai');

const client = new OpenAI({
  baseURL: 'https://api.getalchemystai.com/v1',
  apiKey: process.env.ALCHEMYST_API_KEY,
});

async function chat(message) {
  const response = await client.chat.completions.create({
    model: 'gpt-4o',
    messages: [{ role: 'user', content: message }],
  });
  return response.choices[0].message.content;
}

module.exports = { chat };
""")

        if "memory" in features:
            code_parts.append(
"""
const memoryStore = [];

app.post('/store', (req, res) => {
  memoryStore.push(req.body.data);
  res.json({ status: 'stored' });
});

app.get('/retrieve', (req, res) => {
  res.json({ data: memoryStore });
});
""")

    elif language == "java":
        if feature == "IntelliChat":
            code_parts.append(
"""import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.*;

@SpringBootApplication
@RestController
public class Application {

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }

    @GetMapping("/chat")
    public String chat() {
        return "Streaming chatbot using IntelliChat";
    }
}
""")

        elif feature == "ContextAPI":
            code_parts.append(
"""import org.springframework.web.bind.annotation.*;
import java.util.*;

@RestController
public class ContextController {

    private final List<Map<String, Object>> contextStore = new ArrayList<>();

    @PostMapping("/context/upload")
    public Map<String, String> upload(@RequestParam String data) {
        Map<String, Object> entry = new HashMap<>();
        entry.put("text", data);
        contextStore.add(entry);
        return Map.of("status", "uploaded");
    }

    @GetMapping("/context/query")
    public Map<String, Object> query(@RequestParam String q) {
        List<Map<String, Object>> results = contextStore.stream()
            .filter(e -> e.get("text").toString().toLowerCase().contains(q.toLowerCase()))
            .limit(3)
            .toList();
        return Map.of("query", q, "results", results);
    }
}
""")

        elif feature == "ContextRouter":
            code_parts.append(
"""// Add openai-java dependency to pom.xml first
import com.openai.client.OpenAIClient;
import com.openai.client.okhttp.OpenAIOkHttpClient;

public class AlchemystClient {

    private final OpenAIClient client = OpenAIOkHttpClient.builder()
        .baseUrl("https://api.getalchemystai.com/v1")
        .apiKey(System.getenv("ALCHEMYST_API_KEY"))
        .build();

    public String chat(String message) {
        return client.chat().completions().create(
            ChatCompletionCreateParams.builder()
                .model("gpt-4o")
                .addUserMessage(message)
                .build()
        ).choices().get(0).message().content().orElse("");
    }
}
""")

    final_code = "\n\n".join(code_parts)

    yield ("code", {"snippet": final_code, "language": language})

    # completion message — emitted as a new assistant turn after the code
    completion_text = (
        f"You now have a working {language} starter integration "
        f"for {feature or use_case}. "
        f"Want me to help you deploy this or extend it with additional features?"
    )
    yield ("token", {"text": completion_text})

    session.stage = "done"
    yield ("done", {"sessionId": session.id})