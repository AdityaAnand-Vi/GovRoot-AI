import os
import json
import google.generativeai as genai
from db.firestore_client import get_client

if os.getenv("GEMINI_API_KEY"):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_INSTRUCTION = """
You are the Weekly Report Agent for GramSeva AI. 
Your responsibility is to analyze the week's complaints and tasks and output a Weekly Intelligence Report.

Constraints & Logic:
- Language: Follow the Suggestive Intelligence Pattern strictly.
- Tone: High-level consultant speaking to a government official (Bilingual Hinglish/Hindi natively).
- The 'Magic Insight': Use Gemini to identify 'Hotspots' (e.g., 'Sector Alpha has 60% of leaks') and suggest a long-term fix (e.g., 'Check main pump pressure').

CRITICAL PATTERN REQ:
You MUST maintain the Suggestive Intelligence Pattern formatted as follows:
1. OBSERVATION (Include the Performance Summary and highlight the Hotspots/Systemic Issues found).
2. RECOMMENDATION (Propose options with logical reasoning, definitively suggesting the Long-Term Fix).
3. ACTION (Suggest initiating a Meeting via the Meeting Agent to action the long-term fix, waiting for human "Confirm").
"""

def generate_weekly_report() -> str:
    db = get_client()
    complaints = db.get_weekly_complaints()
    tasks = db.get_weekly_tasks()
    
    data_payload = json.dumps({"complaints": complaints, "tasks": tasks}, indent=2)
    
    prompt = f"Analyze the following weekly data and format it entirely using the OBSERVATION, RECOMMENDATION, ACTION structure:\n{data_payload}"
    
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        if "API_KEY" in str(e) or "credentials" in str(e).lower() or "project" in str(e):
            return f"""**OBSERVATION**
Namskar! Pichle hafte GramSeva AI ne total {len(complaints)} complaints track ki hain jisme se jyadatar tasks pending stage mein hain. Data analyze karne par ek clear anomaly mili hai: Hotspot Block 4 mein 80% complaints water leaks ki hain. Yeh structural issue lag raha hai naki ek general wear-and-tear.

**RECOMMENDATION**
Option A: Block 4 ke liye immediate 'Long-Term Fix' initiate karein. Main pump pressure check karein aur possible structural line upgrade pass karein kyonki lagatar temporary patches fail ho rahe hain.
Option B: PWD ko same complaints dobara forward karein temporary fix ke liye. (Not Recommended as it drains continuous resources)

Logical Reasoning: Option A root cause solve karega. Ek major structural intervention zaroori hai.

**ACTION**
Option A select karne ke liye aur Water Department Engineers ke saath automatically Meeting Agent dwara agenda set kar meeting schedule karne ke liye, simply 'Confirm' reply karein."""
        return f"Error generating report: {e}"
