from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from .agent import root_agent

SESSION_SERVICE = InMemorySessionService()

AGENT_RUNNER = Runner(
    agent=root_agent,
    app_name="ICD-10",
    session_service=SESSION_SERVICE
)
