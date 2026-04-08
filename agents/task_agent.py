"""Google Tasks via MCP."""
from mcp_servers.tasks_server import _draft_task_impl

def manage_task(issue_type: str, details: str) -> str:
    """
    Drafts a task using Google Tasks MCP based on issue scope.
    """
    lower_issue = issue_type.lower()
    assignee = "General Administration"
    
    if 'water' in lower_issue or 'pipe' in lower_issue:
        assignee = "Field Technical Team"
    elif 'road' in lower_issue or 'pothole' in lower_issue:
        assignee = "PWD"
    elif 'electricity' in lower_issue or 'sparking' in lower_issue or 'transformer' in lower_issue:
        assignee = "Electricity Board"
        
    title = f"Emergency: {issue_type} Issue"
    description = f"Details: {details}"
    
    # Push to local data memory overlay so Report Agent catches it
    from db.firestore_client import get_client
    db = get_client()
    db.add_task({"id": "task_auto", "assignee": assignee, "title": title, "status": "Draft", "location": "Unknown"})
    
    # Simulating the exact MCP call
    result = _draft_task_impl(title=title, description=description, assignee=assignee)
    return result
