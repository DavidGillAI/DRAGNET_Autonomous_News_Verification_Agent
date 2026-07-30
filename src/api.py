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
            "validation_passed": result["validation_passed"],
            "research_iterations": result["research_iteration_count"],
        }

    except Exception as e:
        import traceback

        return {
            "error": str(e),
            "traceback": traceback.format_exc(),
        }