from __future__ import annotations
from app.models.session import SessionState
from app.agent.stages.discover import run_discover
from app.agent.stages.match import run_match
from app.agent.stages.generate import run_generate


class AgentLoop:
    def __init__(self, session: SessionState):
        self.session = session

    async def run(self, user_message: str):
        # reset fully when re-entering after a completed session
        if self.session.stage == "done":
            self.session.stage = "discover"
            self.session.integration.no_op = False
            self.session.integration.feature = None
            self.session.integration.stack = None
            self.session.integration.architecture = None

        self.session.history.append({
            "role": "user",
            "content": user_message
        })

        # discover always runs first
        if self.session.stage == "discover":
            async for e in run_discover(self.session):
                yield e

        # match runs only if discover advanced the stage
        if self.session.stage == "match":
            async for e in run_match(self.session):
                yield e

        # generate runs if match advanced or no_op triggered
        if self.session.stage == "generate":
            async for e in run_generate(self.session):
                yield e