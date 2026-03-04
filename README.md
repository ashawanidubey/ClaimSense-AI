# ClaimSense-AI

ClaimSense-AI is an AI-powered claims intelligence assistant that helps healthcare teams convert denied claims into actionable appeal workflows in minutes.

![Python](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![AI](https://img.shields.io/badge/AI-LLM-purple)
![Healthcare](https://img.shields.io/badge/Healthcare-HL7%20%7C%20FHIR-blue)
![License](https://img.shields.io/badge/license-MIT-orange)

## Problem Statement
Healthcare providers lose significant revenue due to denied claims, manual rework, and delayed appeals. Current denial-management workflows are often:
- Labor intensive (manual chart/document review)
- Inconsistent (analyst-to-analyst variation)
- Slow (appeals drafted too late to maximize recovery)
- Expensive (high administrative overhead)

The result: delayed cash flow, preventable write-offs, and operational strain on revenue cycle teams.

## Solution Overview
ClaimSense-AI automates key denial-response steps:
1. Ingests a claim document
2. Parses core claim metadata (Claim ID, Denial Code, Amount, CPT, ICD)
3. Generates an AI denial explanation
4. Produces a draft appeal letter ready for review/submission

This shortens time-to-appeal, standardizes output quality, and helps teams recover revenue faster.

## Architecture Explanation
ClaimSense-AI uses a modular backend + lightweight frontend architecture designed for rapid deployment and extensibility.

### Flow
1. User uploads claim text/document in Streamlit UI
2. Frontend calls `POST /analyze-claim/` (FastAPI)
3. `claim_agent` orchestrates parsing + LLM generation
4. Parser extracts structured fields
5. Azure OpenAI generates:
   - Denial explanation
   - Appeal letter
6. API returns structured JSON to frontend for display

### Component Breakdown
- `frontend/streamlit_app.py`
  - Minimal UI for upload + results visualization
- `app/main.py`
  - FastAPI service exposing analysis endpoint
- `agents/claim_agent.py`
  - Workflow orchestration logic
- `services/claim_parser.py`
  - Rule-based claim field extraction
- `services/llm_service.py`
  - Azure OpenAI integration layer
- `config/settings.py`
  - Environment-driven configuration

## Tech Stack
- Python 3.10+
- FastAPI (backend API)
- Streamlit (frontend demo app)
- Azure OpenAI (LLM inference)
- Pytest (unit testing)
- Requests (frontend-backend HTTP)

## System Architecture

User (Provider / Billing Team)
↓
Frontend Dashboard (React)
↓
FastAPI Backend
↓
Claim Analyzer Agent
↓
AI Reasoning Engine (Azure OpenAI / Mock LLM)
↓
Denial Risk Prediction
↓
Response to Dashboard

## Setup Instructions
### 1. Clone and enter project
```bash
git clone <your-repo-url>
cd ClaimSense-AI
```

### 2. Create virtual environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install fastapi uvicorn streamlit openai requests pytest python-multipart
```

### 4. Configure environment variables
Set the following variables in your shell or `.env` management workflow:
```bash
AZURE_OPENAI_API_KEY=<your_key>
AZURE_OPENAI_ENDPOINT=<your_endpoint>
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_DEPLOYMENT=<your_deployment_name>
```

### 5. Run backend
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 6. Run frontend
In a new terminal:
```bash
streamlit run frontend/streamlit_app.py
```

## Demo Instructions
### Local Demo Script (5 minutes)
1. Start backend and frontend
2. Open Streamlit app in browser
3. Upload sample claim text file
4. Show parsed claim JSON fields
5. Show AI-generated denial explanation
6. Show generated appeal letter draft
7. Explain how staff can edit and submit appeal

### API Demo (optional)
Use curl/Postman to call backend directly:
```bash
curl -X POST "http://127.0.0.1:8000/analyze-claim/" \
  -F "file=@sample_claim.txt"
```

## Future Enhancements
- OCR + PDF ingestion for scanned EOB/ERA documents
- Payer-specific denial policy knowledge base
- Retrieval-augmented generation for evidence-backed appeals
- Human-in-the-loop review/approval workflows
- Claim outcome tracking and analytics dashboard
- EHR/RCM integration (HL7/FHIR/API adapters)
- Multi-tenant auth, audit trails, and enterprise controls

## Screenshots
> Add screenshots here before final submission.

- `screenshots/upload-screen.png` - Upload interface
- `screenshots/parsed-data.png` - Parsed claim JSON output
- `screenshots/explanation.png` - Denial explanation output
- `screenshots/appeal-letter.png` - Generated appeal letter

## Future Enhancements

- EPIC Bridges integration
- HL7 claim ingestion
- FHIR Claim resource validation
- Multi-agent denial prevention workflow

## Example AI Response

```json
{
  "claim_id": "CLM12345",
  "risk_score": 0.78,
  "denial_reason": "Missing prior authorization",
  "recommendation": "Verify payer authorization before submission",
  "estimated_revenue_risk": "$1250"
}

## Hackathon Pitch Summary
ClaimSense-AI is a practical AI copilot for healthcare revenue recovery. It transforms denial management from a manual back-office burden into a rapid, standardized, and scalable workflow. By combining deterministic claim parsing with Azure OpenAI-generated clinical-financial narratives, the platform enables teams to respond faster, improve appeal quality, and accelerate reimbursement cycles. This positions ClaimSense-AI as a high-impact solution with clear ROI and a credible path to enterprise adoption.

---
Built for fast iteration, measurable financial impact, and real-world RCM operations.
