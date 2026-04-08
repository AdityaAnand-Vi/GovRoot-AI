import os
import json
import re
import vertexai
from vertexai.generative_models import GenerativeModel
from agents.complaint_agent import process_complaint
from agents.task_agent import manage_task
from agents.scheme_agent import evaluate_scheme_eligibility
from agents.meeting_agent import check_meeting_conflicts, manage_meeting

vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT", "cohort-1-hackathon-492502"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
)

def get_model(system_instruction=None):
    return GenerativeModel(
        model_name="gemini-2.5-flash-lite",
        system_instruction=system_instruction
    )

class TriageManager:
    WEIGHTS = {
        "water": 10, "medical": 10, "fire": 10,
        "electricity": 7, "roads": 4, "sanitation": 4,
        "admin": 2, "scheme": 2
    }
    TIE_BREAKER = {"fire": 1, "medical": 2, "water": 3}

    @classmethod
    def score_intents(cls, text: str) -> list:
        text_lower = text.lower()
        found_intents = []
        for intent, weight in cls.WEIGHTS.items():
            if intent in text_lower or (intent == "water" and "pipe" in text_lower) or (intent == "fire" and "aag" in text_lower):
                found_intents.append(intent)
        if not found_intents:
            found_intents.append("admin")
        sorted_intents = sorted(
            found_intents,
            key=lambda x: (-cls.WEIGHTS.get(x, 0), cls.TIE_BREAKER.get(x, 99))
        )
        return [{"intent": i, "weight": cls.WEIGHTS[i], "tie_breaker": cls.TIE_BREAKER.get(i, 99)} for i in sorted_intents]

SYSTEM_INSTRUCTION = """
You are the Orchestrator for GramSeva AI — The Rural Governance Co-pilot.

# LANGUAGE MIRRORING (CRITICAL)
- Detect the language of the user input and respond in that EXACT language
- English input → 100% English response
- Hindi/Hinglish input → 100% Hinglish response
- NEVER mix languages within a single response

# IDENTITY
If greeted or asked who you are, introduce yourself and list services in the user's language.

# OUTPUT FORMAT (STRICTLY MANDATORY)
ALWAYS format every response EXACTLY like this with blank lines between sections:

**OBSERVATION**
[What the backend data says. Be specific. 2-3 sentences.]

**RECOMMENDATION**

Option A [Short Title]: [Clear description]

Option B [Short Title]: [Clear description]

*Logical Reasoning: [One sentence explaining why Option A is preferred]*

**ACTION**
[Tell the user exactly what to type to proceed. Use user's language.]

# RULES
- ALWAYS use **bold markdown** for OBSERVATION, RECOMMENDATION, ACTION headers
- ALWAYS put blank lines between each Option
- NEVER compress into one paragraph
- NEVER hallucinate — base Observation strictly on the Python backend trace
- For Level 1 emergencies use urgent empathetic tone
- For tie-breakers (Fire > Medical > Water) explicitly state the reasoning
"""

def process_query(user_text: str) -> str:
    try:
        # STEP 1: Intent Extraction
        json_extractor_prompt = f"""
        Extract the core intents from this query: "{user_text}".
        Return ONLY valid JSON, no markdown:
        {{"intents": ["water", "electricity", "roads", "fire", "medical", "scheme", "meeting", "other"], "user_mentioned": "string or null"}}
        """
        model_json = get_model()
        res_json = model_json.generate_content(json_extractor_prompt)
        raw_val = res_json.text
        if "```json" in raw_val:
            raw_val = raw_val.split("```json")[1].split("```")[0]
        elif "```" in raw_val:
            raw_val = raw_val.split("```")[1].split("```")[0]
        try:
            parsed_intent = json.loads(raw_val.strip())
        except:
            parsed_intent = {"intents": ["admin"], "user_mentioned": "Unknown"}

        intents_list = parsed_intent.get("intents", [])
        triage_scores = TriageManager.score_intents(user_text)
        highest_score = triage_scores[0]['weight'] if triage_scores else 2

        # STEP 2: Python Tool Router
        tool_results_payload = []
        user_ment = parsed_intent.get("user_mentioned") or "Unknown"

        if "water" in intents_list or "fire" in intents_list or "medical" in intents_list or highest_score == 10:
            res1 = process_complaint(user_name=user_ment, block="Sector Alpha", issue=user_text)
            res2 = manage_task(issue_type=intents_list[0] if intents_list else "water", details=user_text)
            if highest_score == 10:
                res3 = check_meeting_conflicts()
                tool_results_payload.append(f"check_meeting_conflicts: {res3}")
            tool_results_payload.append(f"process_complaint: {res1}")
            tool_results_payload.append(f"manage_task: {res2}")
        elif "scheme" in intents_list:
            from db.firestore_client import get_client
            db = get_client()
            status = db.check_citizen_status(user_name=user_ment, block="Sector Alpha")
            if not status:
                tool_results_payload.append(f"Data Desert Protocol Triggered: Citizen '{user_ment}' not found. Physical Document Verification required.")
            else:
                res = evaluate_scheme_eligibility(user_ment)
                tool_results_payload.append(f"evaluate_scheme_eligibility: {res}")
        elif "meeting" in intents_list:
            time_match = re.search(r"\b(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm))\b", user_text)
            requested_time = time_match.group(1) if time_match else None
            res = manage_meeting("Hotspot Coordination", "Block Pramukh", requested_time=requested_time)
            tool_results_payload.append(f"manage_meeting: {res}")
        else:
            tool_results_payload.append("General Admin intent detected. No specialist agent triggered. Manual intervention required.")

        # STEP 3: Synthesis
        synthesis_prompt = f"""
        Generate a structured GramSeva AI response for this input.

        User Input: "{user_text}"
        Triage Priority Score: {highest_score}/10
        Detected Intents: {intents_list}
        Backend Execution Trace:
        {json.dumps(tool_results_payload, indent=2)}

        CRITICAL: Return the key facts and actions clearly. Do NOT use OBSERVATION/RECOMMENDATION/ACTION headers. Write naturally so the ADK agent can reformat conversationally.
        Use **bold markdown** headers. Put blank lines between Options.
        Mirror the language of the user input exactly.
        Base Observation ONLY on the backend trace above.
        """
        model_synth = get_model(system_instruction=SYSTEM_INSTRUCTION)
        response = model_synth.generate_content(synthesis_prompt)
        return response.text

    except Exception as e:
        return f"Failed to generate synthesis: {e}"
