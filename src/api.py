from fastapi import FastAPI
from src.dragnet_langgraph import dragnet_graph

app = FastAPI()


@app.get("/")
def root():
    return {"message": "DRAGNET API is running"}

@app.post("/investigate")
def investigate(request: dict):
    try:
        query = request.get("query")

        if not query:
            return {"error": "A query is required."}

        result = dragnet_graph.invoke(
            {
                "query": query,
                "iteration_count": 0,
            }
        )

        return {
            "report": result["final_report"],
            "planned_search": result.get("research_query"),
            "validation_passed": result.get("validation_passed", False),
            "research_iterations": result.get("research_iteration_count", 0),
            }



    except Exception as e:
        return {
        "report": f"""# Investigation could not be completed

## Reason

{str(e)}

## What you can try

- Rephrase the question.
- Ask about a more recent event.
- Use more specific keywords.
- Check whether the event has been widely reported.

This is an operational limitation rather than evidence that the claim is true or false.
""",
        "validation_passed": False,
        "research_iterations": 0,
    }