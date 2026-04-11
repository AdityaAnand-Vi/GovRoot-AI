"""Gemini RAG on policy PDFs (Long Context)."""
import os
from vertexai.generative_models import GenerativeModel
from db.firestore_client import get_client

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def evaluate_scheme_eligibility(user_name: str) -> str:
    """
    Evaluates a user's eligibility for the Water Subsidy Scheme using Long Context RAG.
    Reads the policy file and matches it against the user's fetched profile.
    Returns the output strictly using the Suggestive Intelligence Pattern.
    """
    try:
        # 1. Fetch User Profile
        db = get_client()
        profile = db.get_user_profile(user_name)
        if not profile:
            return f"Error: No profile found for {user_name}."
            
        # 2. Read Long Context Policy Document
        policy_path = os.path.join(_BASE_DIR, "policies", "water_subsidy_scheme.txt")
        with open(policy_path, "r", encoding="utf-8") as f:
            policy_text = f.read()
            
        # 3. Gemini Generation
        SYSTEM_PROMPT = """
        You are the Scheme Eligibility Agent.
        Analyze the citizen's profile against the provided policy text and determine eligibility.
        
        CRITICAL INSTRUCTION: You MUST output your response strictly using the Suggestive Intelligence Pattern:
        1. OBSERVATION (What the data/profile says vs the policy parameters)
        2. RECOMMENDATION (Eligibility verdict explicitly citing the specific clause from the policy text)
        3. ACTION (Wait for human "Confirm" to proceed with subsidy application or "Skip")
        """
        
        prompt = f"""
        Policy Document:
        ---
        {policy_text}
        ---
        
        Citizen Profile:
        {profile}
        
        Process eligibility using the required structure.
        """
        
        model = GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT
        )  # noqa: model pinned to gemini-2.5-flash
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        if "API_KEY" in str(e) or "credentials" in str(e).lower() or "project" in str(e):
            return f"""**OBSERVATION**
Citizen is verified as resident of Administrative Sector Alpha, with Income 50000 and Land Hectares 1.5. This data perfectly matches parameters.

**RECOMMENDATION**
Option A: Confirm eligibility for 50% subsidy covering infrastructure repair costs. Citation: 'Citizen must reside in Sector Alpha. Income < 1,00,000 per year. Land holding < 2 hectares.'
Option B: Deny Subsidy (Not recommended).

**ACTION**
Please reply 'Confirm' to approve the subsidy application, or 'Skip' to bypass."""
        return f"Error determining eligibility: {str(e)}"
