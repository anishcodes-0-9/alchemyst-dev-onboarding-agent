from app.agent.stages.discover import run_discover
from app.agent.stages.match import run_match
from app.agent.stages.generate import run_generate


class AgentLoop:
    def __init__(self, session):
        self.session = session

    async def run(self, user_message: str):
        # reset stage if previous run completed
        if self.session.get("stage") == "done":
            self.session["stage"] = "discover"

        # append message
        self.session["history"].append({
            "role": "user",
            "content": user_message
        })

        #  main loop
        while True:
            stage = self.session["stage"]

            if stage == "discover":
                async for e in run_discover(self.session):
                    yield e

            elif stage == "match":
                async for e in run_match(self.session):
                    yield e

            elif stage == "generate":
                async for e in run_generate(self.session):
                    yield e

            elif stage == "done":
                break