# DRAGNET: Autonomous News Research & Verification Agent

**Digital Research Agent Gathering News Evidence Transparently**

*Just the facts, ma’am.*

## Project at a glance

| Question | Answer |
| --- | --- |
| Problem | News research requires comparing evidence, distinguishing reporting from inference and making uncertainty visible. |
| Solution | A LangGraph research workflow connected to GNews, OpenAI Web Search, FastAPI, n8n and Telegram. |
| Output | A structured report with supported and disputed claims, source links and validation feedback. |
| Skills demonstrated | Workflow design, API integration, prompt iteration, evidence handling and evaluation. |
| Current limit | An experimental MVP, with archived reports and separate evaluation exercises; it does not establish the truth of every claim. |

## My contribution and use of AI

I developed DRAGNET using AI assistance for coding and review. My focus was defining the research workflow and verification rules, connecting the services, testing report behaviour and examining failures in uncertainty handling.

The work extends beyond generation: related repositories document claim classification, human review and preliminary governance assessments. Those exercises have their own scope and limitations and are not certifications or an end-to-end accuracy benchmark for this agent.

## See the evidence

| Evidence | What it shows |
| --- | --- |
| [Archived report and validator feedback](outputs/DragnetGraphReport_Did_Donald_Trump_directly_influence_FIFA_s_decision_involvin_2026-07-25_16-14-37.txt) | An example of the report structure and an unresolved draft flagged for further review. It is historical generated output, not a freshly verified news source. |
| [Claim-classification evaluation](https://github.com/DavidGillAI/DRAGNET_LangSmith_Claim_Evaluation/blob/main/evaluation_summary.md) | Prompt refinement improved the recorded result from 11/16 to 14/16 on the same small dataset. Unseen testing is still needed. |
| [Human review in Argilla](https://github.com/DavidGillAI/DRAGNET_Human_in_the_Loop_Evaluation/blob/main/lab_summary.md) | One reviewer's assessment of evidence grounding, consistency, uncertainty and clarity. |
| [GDPR self-assessment](https://github.com/DavidGillAI/DRAGNET_GDPR_Self_Audit) | A preliminary assessment exercise. |
| [EU AI Act assessment](https://github.com/DavidGillAI/DRAGNET_EU_AI_Act_Compliance_Audit) | A separate learning exercise about regulatory considerations. |

## Overview

DRAGNET is an autonomous news research and verification agent. It is designed to investigate a current news story across multiple sources, compare the available reporting, identify unsupported claims, reduce opinion and framing, and return a fact-focused summary with transparent source links.

The project follows the principle:

**Query in → autonomous research and verification → report out**

## Project Status

The repository documents an MVP connected end to end during development. Current live operation has not been reverified for this portfolio update.

A user submits a question through Telegram. n8n sends it to a FastAPI endpoint, where a LangGraph workflow plans the research, retrieves news evidence through GNews, performs secondary verification using OpenAI Web Search, generates and validates a structured report, and returns the result to Telegram.

The exported n8n workflow uses a temporary Cloudflare tunnel address. Configure your own endpoint and credentials before attempting a demonstration.

## Technology Stack

- Python
- OpenAI API and OpenAI Web Search
- LangChain
- LangGraph
- GNews API
- FastAPI and Uvicorn
- n8n
- Telegram Bot API
- Cloudflare Quick Tunnel

## Repository Structure

- `src/dragnet_langgraph.py`  
  The core LangGraph workflow for planning, research, web verification, evidence preparation, report generation, validation and finalisation.

- `src/dragnet_mvp.py`  
  Core GNews retrieval and report-generation functions used by the workflow.

- `src/api.py`  
  The FastAPI application exposing DRAGNET through the `/investigate` endpoint.

- `docs/`  
  Workflow diagrams and development documentation.

- `reference_docs/`  
  Verification rules, source-exclusion guidance and the report template.

- `prompts/`  
  Supporting agent and validation instructions.

- `n8n/`  
  Location for the exported n8n workflow used to connect Telegram to the FastAPI endpoint.

- `project_plan.md`  
  The original project scope, implementation plan, risks and definition of done.

- `requirements.txt`  
  The pinned Python dependencies required to run the project.

## Development Notes

The project plan records the original scope and development decisions. The current implementation and documentation describe the completed MVP.

DRAGNET is designed for transparent evidence synthesis, not absolute truth determination. It reports what the available evidence supports, disputes or leaves uncertain.

Features such as Pinecone, RAG, source credibility scoring, multi-language support and a web dashboard remain future development possibilities.

## Setup

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install the dependencies

```powershell
pip install -r requirements.txt
```

### 3. Create a `.env` file in the project root

```env
GNEWS_API_KEY=your_gnews_api_key
OPENAI_API_KEY=your_openai_api_key
```

Never commit or share the `.env` file.

### 4. Start the FastAPI server

```powershell
uvicorn src.api:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Submit an investigation using a POST request to:

```text
http://127.0.0.1:8000/investigate
```

with a JSON body such as:

```json
{
  "query": "Did a public figure influence a recent sporting decision?"
}
```

The `query` must be a string containing 1–4,000 characters after trimming surrounding whitespace. Invalid requests return HTTP 422 without starting research. An unexpected research failure returns HTTP 500 and a generic report without exposing exception details. A completed workflow can still return HTTP 200 with `validation_passed: false`; this means the report needs review, not that the underlying claim is false.

### Telegram and n8n error handling

The exported workflow enables **Response → Never Error** in its HTTP Request node so the API's error report can still reach the document-delivery step. Request validation and research errors retain a `report` field. Connection failures before an HTTP response still require n8n error handling. Reimport or update the workflow when adopting these API changes; the live Telegram integration has not been retested as part of this update.

### Offline API checks

```powershell
python -m pip install httpx
python -m unittest discover -s tests -v
```

These checks use a fake research graph and make no GNews, OpenAI or Telegram requests. They cover accepted inputs, rejected inputs, response status codes and safe error messages. The older `src/test_*.py` scripts make live provider calls and need credentials; they are separate from these offline checks.
