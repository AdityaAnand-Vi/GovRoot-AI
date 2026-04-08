"""MCP: Google Tasks integration using fastmcp."""
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("GoogleTasksServer")

def _draft_task_impl(title: str, description: str, assignee: str) -> str:
    return f"Task '{title}' drafted successfully for {assignee}. Description: {description}"

@mcp.tool()
def draft_task(title: str, description: str, assignee: str) -> str:
    """
    Drafts a task for a given assignee in the system.
    """
    return _draft_task_impl(title, description, assignee)

def init_tasks_server():
    """Runs the FastMCP server."""
    return mcp
