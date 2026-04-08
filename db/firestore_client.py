"""Firestore CRUD helpers."""

# Mock Database
# Sector: Administrative Sector Alpha
MOCK_USERS = {
    "User_A": {"id": "ID-001", "sector": "Administrative Sector Alpha", "status": "Active Citizen", "income": 50000, "land_hectares": 1.5},
    "User_B": {"id": "ID-002", "sector": "Administrative Sector Alpha", "status": "Active Citizen", "income": 120000, "land_hectares": 2.5},
    "User_C": {"id": "ID-003", "sector": "Administrative Sector Alpha", "status": "Active Citizen", "income": 80000, "land_hectares": 1.0}
}

MOCK_COMPLAINTS = [
    {"id": "comp_1", "user": "User_A", "issue": "Water pipe burst, massive leak", "location": "Block 4", "status": "Open", "timestamp": "2 days ago"},
    {"id": "comp_2", "user": "User_B", "issue": "No water pressure, pipe leaking on street", "location": "Block 4", "status": "Open", "timestamp": "3 days ago"},
    {"id": "comp_3", "user": "User_C", "issue": "Main line water leak", "location": "Block 4", "status": "Open", "timestamp": "1 day ago"},
    {"id": "comp_4", "user": "User_A", "issue": "Water pooling outside house due to broken supply", "location": "Block 4", "status": "Pending", "timestamp": "4 days ago"},
    {"id": "comp_5", "user": "Unknown", "issue": "Continuous water flowing from broken joint", "location": "Block 4", "status": "Pending", "timestamp": "Today"},
    {"id": "comp_6", "user": "User_B", "issue": "Pothole filled with water", "location": "Block 2", "status": "Closed", "timestamp": "6 days ago"}
]

MOCK_TASKS = [
    {"id": "task_1", "assignee": "Field Technical Team", "title": "Emergency: Water Supply", "status": "Draft", "location": "Block 4"},
    {"id": "task_2", "assignee": "PWD", "title": "Fill pothole", "status": "Completed", "location": "Block 2"}
]

LOCAL_DB_UPDATES = []

def get_client():
    """Returns a mock firestore client wrapper."""
    class MockFirestoreClient:
        def check_citizen_status(self, user_name: str, block: str):
            user = MOCK_USERS.get(user_name)
            if user:
                return user["status"]
            return None
            
        def get_user_profile(self, user_name: str):
            return MOCK_USERS.get(user_name)
            
        def get_weekly_complaints(self):
            return MOCK_COMPLAINTS
            
        def get_weekly_tasks(self):
            return MOCK_TASKS + LOCAL_DB_UPDATES
            
        def add_task(self, task_dict: dict):
            LOCAL_DB_UPDATES.append(task_dict)
            
    return MockFirestoreClient()
