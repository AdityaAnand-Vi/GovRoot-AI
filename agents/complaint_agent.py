"""Complaint logging + priority."""
from db.firestore_client import get_client

def process_complaint(user_name: str, block: str, issue: str) -> str:
    """
    Checks citizen status in the block.
    If the record is missing, it triggers the Data Desert Protocol.
    Otherwise, acknowledges the complaint.
    """
    db = get_client()
    status = db.check_citizen_status(user_name=user_name, block=block)
    
    if not status:
        return f"Data Desert Protocol Triggered: Citizen record for '{user_name}' not found in '{block}'. You MUST suggest an 'Official Paper Record' base 'Physical Document Verification'."
    
    return f"Citizen {user_name} verified ({status}). Complaint regarding '{issue}' is valid in {block}."
