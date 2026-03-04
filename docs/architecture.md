# ClaimSense-AI System Architecture

## 1. Purpose and Scope
This document describes the architecture of ClaimSense-AI, a healthcare revenue-cycle assistant that ingests claim text, extracts structured claim attributes, and generates denial insights plus appeal-letter drafts using Azure OpenAI.

Goals:
- Keep API integration simple for internal tools and demos
- Separate deterministic parsing from generative reasoning
- Enable secure, production-grade deployment on Azure

## 2. High-Level Architecture
ClaimSense-AI is organized into four layers:

1. Presentation Layer
- `frontend/streamlit_app.py`
- Provides a minimal UI for file upload and result rendering

2. API Layer
- `app/main.py` (FastAPI)
- Exposes `POST /analyze-claim/` for claim analysis
- Handles file ingestion, validation, and response shaping

3. Agent/Domain Layer
- `agents/claim_agent.py`
- Orchestrates parsing and prompt-driven generation
- Produces standardized output JSON

4. Service/Integration Layer
- `services/claim_parser.py` for rule-based extraction
- `services/llm_service.py` for Azure OpenAI calls
- `config/settings.py` for environment-driven config

## 3. FastAPI Backend Design
### 3.1 API Contract
Endpoint:
- `POST /analyze-claim/`

Input:
- Multipart form-data with `file` (`UploadFile`)

Output (JSON):
- `status`: processing status
- `filename`: uploaded file name
- `analysis`:
  - `parsed_data`
  - `explanation`
  - `appeal_letter`

### 3.2 Backend Responsibilities
- Validate upload metadata and payload size
- Decode content safely (UTF-8)
- Delegate business workflow to `process_claim`
- Normalize errors into HTTP responses

### 3.3 Error Strategy
- `400`: invalid/empty/decode-failed uploads
- `413`: payload exceeds configured limit
- `500`: unexpected internal failures

## 4. Agent Orchestration Layer
`process_claim(file_text: str)` in `agents/claim_agent.py` implements a clear 4-step flow:

1. Parse claim content into deterministic fields
2. Build denial-explanation prompt from parsed fields
3. Build appeal-letter prompt using parsed fields + explanation
4. Return consolidated response object

Design rationale:
- Keeps orchestration centralized and testable
- Avoids prompt logic in API handlers
- Supports future multi-agent patterns (review agent, compliance agent, etc.)

## 5. Azure OpenAI Integration
### 5.1 Client Strategy
`services/llm_service.py` uses `AzureOpenAI` with a cached client (`lru_cache`) to reduce client reinitialization overhead.

### 5.2 Configuration
Credentials and model settings are read from `config/settings.py` via environment variables:
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_VERSION`
- `AZURE_OPENAI_DEPLOYMENT`

### 5.3 Invocation Pattern
`call_llm(prompt: str) -> str`:
- Sends a system instruction: "You are a healthcare revenue cycle expert."
- Sends the user prompt as contextual input
- Calls `chat.completions.create`
- Returns text content only
- Logs and safely degrades on failure

## 6. End-to-End Data Flow
1. User uploads claim file via Streamlit UI
2. Frontend sends multipart request to FastAPI endpoint
3. FastAPI validates and reads file content
4. `claim_agent.process_claim()` is called
5. Parser extracts structured fields (`claim_id`, `denial_code`, `amount`, `cpt`, `icd`)
6. LLM call #1 generates denial explanation
7. LLM call #2 generates appeal letter
8. API returns structured analysis JSON
9. Frontend renders parsed data + generated narratives

## 7. Security Considerations
### 7.1 Secrets Management
- Do not hardcode credentials
- Load secrets from environment variables
- For production, use Azure Key Vault-backed secret injection

### 7.2 Data Protection
- Treat uploaded claim text as sensitive healthcare-adjacent data
- Enforce TLS in all non-local environments
- Avoid logging raw PHI/PII content
- Implement retention policy for request payloads and logs

### 7.3 API Hardening
- Add authentication (Azure AD / OAuth2 / API Gateway token)
- Add request size and rate limits
- Validate content type and sanitize unexpected input
- Enable CORS only for trusted origins

### 7.4 Operational Controls
- Centralized audit logs (access + errors)
- Alerting on error spikes, timeouts, and anomalous traffic
- Dependency and container image scanning in CI/CD

## 8. Future Azure Deployment Architecture
Target production topology:

1. Edge and Routing
- Azure Front Door or Application Gateway (WAF-enabled)

2. Compute
- FastAPI backend on Azure Container Apps or AKS
- Streamlit frontend on Azure App Service / Container Apps

3. AI and Secrets
- Azure OpenAI for inference
- Azure Key Vault for secrets

4. Storage and Observability
- Azure Blob Storage for optional document persistence
- Azure Monitor + Application Insights for telemetry
- Log Analytics workspace for queryable audit trails

5. Network Security
- Private endpoints for Azure OpenAI/Key Vault where possible
- VNet integration and NSG policies

6. Delivery Pipeline
- GitHub Actions or Azure DevOps
- Build, test, containerize, scan, deploy
- Blue/green or canary deployment strategy

## 9. Scalability and Reliability Notes
- Horizontal scaling via container replicas
- Add asynchronous job queue for large document or batch processing
- Add retries and circuit-breaking around LLM calls
- Cache repeat requests where clinically and operationally appropriate

## 10. Open Design Extensions
- Add OCR service for PDF/image claims
- Add payer policy retrieval (RAG) for grounded explanations
- Add human approval workflow before outbound appeal generation
- Add metrics layer (denial category trends, recovery forecasting)
