import sys
import json
import traceback

def run_tests():
    print("--- STARTING TESTS ---")
    
    print("\n[1] Testing Firestore Data Persistence Layer")
    try:
        from db.firestore_client import get_client
        db = get_client()
        status_valid = db.check_citizen_status("User_A", "Sector Alpha")
        status_invalid = db.check_citizen_status("Ghost_User", "Sector Alpha")
        print(f"User_A Status: {status_valid}")
        print(f"Ghost_User Status: {status_invalid}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n[2] Testing Complaint Agent")
    try:
        from agents.complaint_agent import process_complaint
        complaint_res = process_complaint("User_A", "Sector Alpha", "Broken Pipe")
        print(f"Result: {complaint_res}")
        complaint_miss = process_complaint("Ghost_User", "Sector Alpha", "Broken Pipe")
        print(f"Data Desert Result: {complaint_miss}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n[3] Testing Task Agent (with Local Persistence)")
    try:
        from agents.task_agent import manage_task
        task_res = manage_task("road", "Massive pothole on Main St")
        print(f"Result: {task_res}")
        # Validate persistence
        from db.firestore_client import get_client
        db = get_client()
        tasks = db.get_weekly_tasks()
        print(f"Total tasks in local memory now: {len(tasks)}")
        print(f"Locally persisted task: {tasks[-1]}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n[4] Testing Meeting Agent (FastMCP)")
    try:
        from agents.meeting_agent import manage_meeting
        meet_res = manage_meeting("Hotspot Coordination", "Block Pramukh")
        print(f"Agent Output: {meet_res}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n[5] Testing Orchestrator /process_query (Without API Key Failsafe)")
    try:
        from agents.orchestrator import process_query
        query_res = process_query("Someone is playing loud music at night")
        print("\n--- Fallback Synthetic Output Generated ---")
        print(query_res)
    except Exception as e:
        print(f"Error: {e}")
        
    print("\n[6] Testing Report Agent /generate_weekly_report (Without API Key Failsafe)")
    try:
        from agents.report_agent import generate_weekly_report
        rep_res = generate_weekly_report()
        print("\n--- Fallback Synthetic Output Generated ---")
        print(rep_res)
    except Exception as e:
        print(f"Error: {e}")

    print("\n[7] Scenario 1: The High-Stakes Triage (Multilingual)")
    try:
        from agents.orchestrator import process_query
        res = process_query("Sector Alpha mein Aag lagi hai (Fire) aur Block 4 mein bijli chali gayi hai. Jaldi batao kya karein?")
        print(res)
    except Exception as e:
        print(f"Error: {e}")

    print("\n[8] Scenario 2: The Data Desert & Scheme Flow")
    try:
        from agents.orchestrator import process_query
        res = process_query("Check if User_Z is eligible for the water subsidy scheme.")
        print(res)
    except Exception as e:
        print(f"Error: {e}")

    print("\n[9] Scenario 3: The Systemic Insight (The Report)")
    try:
        from agents.report_agent import generate_weekly_report
        res = generate_weekly_report()
        print(res)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_tests()
