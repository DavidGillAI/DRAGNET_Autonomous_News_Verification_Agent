import logging
from typing import Annotated

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, StringConstraints

from src.dragnet_langgraph import dragnet_graph

app = FastAPI(title="DRAGNET")
logger = logging.getLogger(__name__)


class InvestigationRequest(BaseModel):
    query: Annotated[
        str,
        StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=4000),
    ]


def failure_response(message: str, status_code: int) -> JSONResponse:
    # Keep the report field for the n8n document-delivery workflow.
    return JSONResponse(
        status_code=status_code,
        content={
            "report": (
                "# Investigation could not be completed\n\n"
                f"{message}\n\n"
                "This is an operational limitation rather than evidence "
                "that the claim is true or false."
            ),
            "validation_passed": False,
            "research_iterations": 0,
        },
    )


@app.exception_handler(RequestValidationError)
async def invalid_request(request: Request, error: RequestValidationError):
    return failure_response(
        'Send a JSON object with a "query" string containing 1–4,000 characters.',
        422,
    )


@app.get("/")
def root():
    return {"message": "DRAGNET API is running"}

@app.post("/investigate")
def investigate(request: InvestigationRequest):
    try:
        result = dragnet_graph.invoke(
            {
                "query": request.query,
                "iteration_count": 0,
            }
        )

        return {
            "report": result["final_report"],
            "planned_search": result.get("research_query"),
            "validation_passed": result.get("validation_passed", False),
            "research_iterations": result.get("research_iteration_count", 0),
        }
    except Exception as error:
        # Exception messages may contain provider URLs or credentials.
        logger.error("Investigation failed (%s)", type(error).__name__)
        return failure_response(
            "The research service could not complete this request. "
            "Please try again later or rephrase your question.",
            500,
        )
