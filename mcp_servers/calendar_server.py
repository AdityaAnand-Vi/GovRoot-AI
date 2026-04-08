"""MCP: Google Calendar integration using fastmcp."""
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("GoogleCalendarServer")

def _schedule_meeting_impl(title: str, start_time: str, attendees: str) -> str:
    # Explicit logging format requested for technical demo
    print(f"\n[MCP TRIGGER] Google Calendar Server -> schedule_meeting() invoked!")
    str_log = f"Meeting '{title}' scheduled for {start_time}. Attendees: {attendees}."
    print(str_log)
    return str_log

@mcp.tool()
def schedule_meeting(title: str, start_time: str, attendees: str) -> str:
    """
    Drafts and schedules a calendar event.
    """
    return _schedule_meeting_impl(title, start_time, attendees)

def init_calendar_server():
    """Runs the FastMCP server."""
    return mcp
