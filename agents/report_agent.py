import json
from vertexai.generative_models import GenerativeModel
from db.firestore_client import get_client

# vertexai.init() is called once at startup in orchestrator.py

SYSTEM_INSTRUCTION = """
You are the Weekly Report Agent for GovRoot AI. 
Your responsibility is to analyze the week's complaints and tasks and output a Weekly Intelligence Report.

Constraints & Logic:
- Language: Follow the Suggestive Intelligence Pattern strictly.
- Tone: High-level consultant speaking to a government official (Bilingual Hinglish/Hindi natively).
- The 'Magic Insight': Identify 'Hotspots' and suggest a long-term fix.

CRITICAL PATTERN:
1. OBSERVATION (Performance Summary and Hotspots).
2. RECOMMENDATION (Options with logical reasoning and Long-Term Fix).
3. ACTION (Suggest initiating a Meeting, wait for human Confirm).
"""

def generate_weekly_report() -> str:
    db = get_client()
    complaints = db.get_weekly_complaints()
    tasks = db.get_weekly_tasks()
    
    data_payload = json.dumps({"complaints": complaints, "tasks": tasks}, indent=2)
    prompt = f"Analyze the following weekly data using OBSERVATION, RECOMMENDATION, ACTION structure:\n{data_payload}"
    
    try:
        model = GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating report: {e}"
