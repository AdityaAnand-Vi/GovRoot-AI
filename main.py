import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents.orchestrator import process_query
from agents.report_agent import generate_weekly_report

app = FastAPI(title="GovRoot AI — Multi-Agent Governance System", description="AI-powered multi-agent system for rural governance", version="1.0.0")

@app.get("/")
def root():
    return {"service": "GovRoot AI", "status": "running", "docs": "/docs"}

class QueryRequest(BaseModel):
    text: str = "Block 4 mein paani ki problem hai aur meeting fix karo"

@app.post("/query")
async def query_endpoint(request: QueryRequest):
    """
    Single endpoint to handle user inputs.
    Routes the query to the Orchestrator for intent extraction and routing.
    """
    try:
        response_text = process_query(request.text)
        return {"status": "success", "response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/report")
async def report_endpoint():
    """
    Generates the Weekly Intelligence Report utilizing the ReportAgent.
    """
    try:
        report_text = generate_weekly_report()
        return {"status": "success", "report": report_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
