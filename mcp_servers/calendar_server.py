"""MCP: Google Calendar integration using fastmcp."""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("GoogleCalendarServer")

def _schedule_meeting_impl(title: str, start_time: str, attendees: str) -> str:
    print(f"\n[MCP TRIGGER] Google Calendar Server -> schedule_meeting() invoked!")
    str_log = f"Meeting '{title}' scheduled for {start_time} (10:00 AM Morning slot). Attendees: {attendees}."
    print(str_log)
    return str_log

@mcp.tool()
def schedule_meeting(title: str, start_time: str, attendees: str) -> str:
    """Drafts and schedules a calendar event."""
    return _schedule_meeting_impl(title, start_time, attendees)

def init_calendar_server():
    return mcp
