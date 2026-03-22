import asyncio


class AgentLoop:
    def __init__(self, session):
        self.session = session

    async def run(self, user_message: str):
        # store user message
        self.session["history"].append({
            "role": "user",
            "content": user_message
        })

        while True:
            stage = self.session["stage"]

            if stage == "discover":
                async for e in self._discover():
                    yield e

            elif stage == "match":
                async for e in self._match():
                    yield e

            elif stage == "generate":
                async for e in self._generate():
                    yield e

            elif stage == "done":
                break

    async def _discover(self):
        text = "What are you building?"

        for ch in text:
            yield ("token", {"text": ch})
            await asyncio.sleep(0.01)

        self.session["integration"]["useCase"] = "chatbot"
        self.session["stage"] = "match"

        yield (
            "stage_update",
            {
                "stage": "match",
                "integration": self.session["integration"]
            }
        )

    async def _match(self):
        self.session["integration"]["feature"] = "IntelliChat"
        self.session["stage"] = "generate"

        yield (
            "stage_update",
            {
                "stage": "generate",
                "integration": self.session["integration"]
            }
        )

    async def _generate(self):
        code = "print('Hello from Alchemyst')"

        yield (
            "code",
            {
                "snippet": code,
                "language": "python"
            }
        )

        self.session["stage"] = "done"

        yield (
            "done",
            {"sessionId": self.session["id"]}
        )