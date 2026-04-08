from google.adk.agents import Agent
from agents.orchestrator import process_query
from agents.report_agent import generate_weekly_report

def query_tool(text: str) -> str:
    """Send a query to GramSeva AI orchestrator."""
    return process_query(text)

def report_tool() -> str:
    """Generate the weekly intelligence report."""
    return generate_weekly_report()

root_agent = Agent(
    name="govroot_ai",
    model="gemini-2.0-flash",
    description="GramSeva AI — Rural Governance Co-pilot for Gram Panchayat Secretaries.",
    instruction="""
    You are GramSeva AI, a rural governance co-pilot.
    Use query_tool for any governance queries, complaints, scheme checks, or meetings.
    Use report_tool when the user asks for a weekly report.
    Always respond in the same language as the user (English or Hinglish).
    """,
    tools=[query_tool, report_tool],
)
