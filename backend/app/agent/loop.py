from __future__ import annotations
from app.models.session import SessionState
from app.agent.stages.discover import run_discover
from app.agent.stages.match import run_match
from app.agent.stages.generate import run_generate


class AgentLoop:
    def __init__(self, session: SessionState):
        self.session = session

    async def run(self, user_message: str):
        # reset if session completed
        if self.session.stage == "done":
            self.session.stage = "discover"
            self.session.integration.no_op = False
            self.session.integration.feature = None
            self.session.integration.stack = None
            self.session.integration.architecture = None
            self.session.integration.features = []

        valid_stages = {"discover", "match", "generate", "done"}
        if self.session.stage not in valid_stages:
            self.session.stage = "discover"

        self.session.history.append({
            "role": "user",
            "content": user_message
        })

        current_stage = self.session.stage

        while current_stage in ["discover", "match", "generate"]:
            if current_stage == "discover":
                async for e in run_discover(self.session):
                    yield e

            elif current_stage == "match":
                async for e in run_match(self.session):
                    yield e

            elif current_stage == "generate":
                async for e in run_generate(self.session):
                    yield e
                break

            if self.session.stage == current_stage:
                break

            current_stage = self.session.stage