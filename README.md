# DRAGNET: Autonomous News Research & Verification Agent

**Digital Research Agent Gathering News Evidence Transparently**

*Just the facts, ma’am.*

## Overview

DRAGNET is an autonomous news research and verification agent. It is designed to investigate a current news story across multiple sources, compare the available reporting, identify unsupported claims, reduce opinion and framing, and return a fact-focused summary with transparent source links.

The project follows the principle:

**Query in → autonomous research and verification → report out**

## Project Status

The DRAGNET MVP is complete and operational end to end.

A user submits a question through Telegram. n8n sends it to a FastAPI endpoint, where a LangGraph workflow plans the research, retrieves news evidence through GNews, performs secondary verification using OpenAI Web Search, generates and validates a structured report, and returns the result to Telegram.

The current focus is final testing, documentation and presentation preparation.

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