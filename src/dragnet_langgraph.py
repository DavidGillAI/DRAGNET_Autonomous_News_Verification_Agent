from typing import TypedDict
import re
from datetime import datetime
from langgraph.graph import END, START, StateGraph
from dragnet_mvp import (
    PROJECT_ROOT,
    agent_checklist,
    build_system_prompt,
    fetch_gnews_articles,
    format_articles_for_llm,
    generate_dragnet_report,
    llm,
)

MAX_DRAFT_ITERATIONS = 3
MAX_RESEARCH_ITERATIONS = 3

class DragnetState(TypedDict, total=False):
    query: str
    articles: list[dict]
    evidence_package: str
    draft_report: str
    validation_feedback: str
    iteration_count: int
    final_report: str
    validation_passed: bool
    research_query: str
    research_iteration_count: int
    research_log: list[str]

def research_node(state: DragnetState):
    search_query = state.get("research_query", state["query"])
    print(f"\nResearching GNews query: {search_query}")
    new_articles = fetch_gnews_articles(search_query)

    existing_articles = state.get("articles", [])

    articles_by_url = {
        article.get("url"): article
        for article in existing_articles
        if article.get("url")
    }

    previous_unique_count = len(articles_by_url)

    for article in new_articles:
        article_url = article.get("url")

        if article_url:
            articles_by_url[article_url] = article

    combined_articles = list(articles_by_url.values())

    if not combined_articles:
        raise ValueError("GNews returned no articles for this investigation.")

    research_entry = (
        f"Query: {search_query} | "
        f"Results returned: {len(new_articles)} | "
        f"Unique articles added: "
        f"{len(combined_articles) - previous_unique_count} | "
        f"Total unique articles: {len(combined_articles)}"
        
    )
    return {
        "articles": combined_articles,
        "research_iteration_count": (
            state.get("research_iteration_count", 0) + 1
        ),
        "research_log": state.get("research_log", []) + [research_entry],

    
    }

def prepare_evidence_node(state: DragnetState):
    evidence_package = format_articles_for_llm(state["articles"])

    return {
        "evidence_package": evidence_package,
    }

def generate_draft_node(state: DragnetState):
    research_log_text = "\n".join(state.get("research_log", []))

    evidence_with_context = f"""
{state["evidence_package"]}

Verified research process:
Research iterations completed: {state["research_iteration_count"]}
{research_log_text}

Use these details in Research Transparency where relevant.
Do not claim that sources are independent, unbiased, duplicated or syndicated
unless the evidence explicitly establishes that.
""".strip()

    draft_report = generate_dragnet_report(
        state["query"],
        evidence_with_context,
    )

    return {
        "draft_report": draft_report,
        "iteration_count": state.get("iteration_count", 0) + 1,
    }

def validate_draft_node(state: DragnetState):
    research_log_text = "\n".join(state.get("research_log", []))
    review_prompt = f"""
Review this DRAGNET draft against the checklist.

Checklist:
{agent_checklist}

Important:
- Check whether claims are classified cautiously.
- Check whether single-source or second-hand claims are treated appropriately.
- Check whether every source used in the report has complete metadata.
- Check whether the report invents facts, access details or research actions.

Respond with exactly one of these statuses on the first line:
STATUS: PASS
STATUS: REVISE

After the status, briefly explain any problems.

Verified runtime research record:
Research iterations completed: {state["research_iteration_count"]}
{research_log_text}

Use this runtime record when assessing research actions and recency.
Do not assume different publications are independent evidence chains unless
the supplied evidence establishes that.

Evidence package used for this report:
{state["evidence_package"]}

Compare the draft only against this supplied evidence and the verified runtime
record. Do not require information that is unavailable from these inputs.

Draft report:
{state["draft_report"]}
""".strip()

    response = llm.invoke(review_prompt)
    feedback = response.content.strip()

    return {
        "validation_feedback": feedback,
        "validation_passed": feedback.startswith("STATUS: PASS"),
    }

def plan_follow_up_research_node(state: DragnetState):
    current_date = datetime.now().strftime("%d %B %Y")
    research_log_text = "\n".join(state.get("research_log", []))
    planning_prompt = f"""
Create one concise follow-up news search query that could address the most
important evidence gap identified by the validator.

Original user query:
{state["query"]}

Validation feedback:
{state["validation_feedback"]}

Previous searches:
{research_log_text}

Current date:
{current_date}

Requirements:
- Use 3 to 8 specific search terms.
- Target one missing fact, corroborating source or primary source.
- Use the current year when a recency term is useful.
- Do not invent or use an earlier date unless it appears in the evidence.
- Do not repeat or closely paraphrase a previous search query.
- Avoid vague phrases such as "latest independent analysis".
- Return only the search query.


""".strip()

    response = llm.invoke(planning_prompt)
    follow_up_query = response.content.strip().strip('"')
    print(f"Planned follow-up query: {follow_up_query}")

    return {
        "research_query": follow_up_query,
    }

def revise_draft_node(state: DragnetState):
    research_log_text = "\n".join(state.get("research_log", []))
    revision_prompt = f"""
{build_system_prompt()}

Revise the DRAGNET report using the validation feedback.

User query:
{state["query"]}

Evidence package:
{state["evidence_package"]}

Verified research process:
Research iterations completed: {state["research_iteration_count"]}
{research_log_text}

Use these details in Research Transparency where relevant.
Do not claim that sources are independent, unbiased, duplicated or syndicated
unless the evidence explicitly establishes that.

Current draft:
{state["draft_report"]}

Validation feedback:
{state["validation_feedback"]}

Return the complete corrected report only.
""".strip()

    response = llm.invoke(revision_prompt)

    return {
        "draft_report": response.content,
        "iteration_count": state["iteration_count"] + 1,
    }

def decide_after_validation(state: DragnetState):
    if state["validation_passed"]:
        return "finish"

    if state["iteration_count"] >= MAX_DRAFT_ITERATIONS:
        return "finish"

    if state["research_iteration_count"] >= MAX_RESEARCH_ITERATIONS:
        return "finish"

    return "research_more"

def decide_after_evidence(state: DragnetState):
    if state.get("iteration_count", 0) == 0:
        return "generate"

    return "revise"

def finalise_report_node(state: DragnetState):
    final_report = state["draft_report"]

    if not state["validation_passed"]:
        final_report += f"""

---

## Automated Validation Warning

This report did not pass DRAGNET's automated validation after
{state["iteration_count"]} draft iterations and
{state["research_iteration_count"]} research iterations.

Treat this output as an unresolved draft requiring further research or review.

Outstanding validation feedback:

{state["validation_feedback"]}
""".rstrip()

    return {
        "final_report": final_report,
    }

workflow = StateGraph(DragnetState)

workflow.add_node("research", research_node)
workflow.add_node("prepare_evidence", prepare_evidence_node)
workflow.add_node("generate_draft", generate_draft_node)
workflow.add_node("validate_draft", validate_draft_node)
workflow.add_node("plan_follow_up_research", plan_follow_up_research_node)
workflow.add_node("revise_draft", revise_draft_node)
workflow.add_node("finalise_report", finalise_report_node)

workflow.add_edge(START, "research")
workflow.add_edge("research", "prepare_evidence")

workflow.add_conditional_edges(
    "prepare_evidence",
    decide_after_evidence,
    {
        "generate": "generate_draft",
        "revise": "revise_draft",
    },
)

workflow.add_edge("generate_draft", "validate_draft")
workflow.add_edge("revise_draft", "validate_draft")

workflow.add_conditional_edges(
    "validate_draft",
    decide_after_validation,
    {
        "research_more": "plan_follow_up_research",
        "finish": "finalise_report",
    },
)

workflow.add_edge("plan_follow_up_research", "research")
workflow.add_edge("finalise_report", END)

dragnet_graph = workflow.compile()

def main():
    print("DRAGNET LangGraph workflow loaded successfully.")

    query = input("Enter a news story or search query: ").strip()

    if not query:
        raise ValueError("A news query is required.")

    print(f"Researching: {query}")

    result = dragnet_graph.invoke(
        {
            "query": query,
            "iteration_count": 0,
        }
    )

    report = result["final_report"]

    print("\nDRAGNET LANGGRAPH REPORT\n")
    print(report)
    print(f"\nDraft iterations completed: {result['iteration_count']}")
    print(
    f"Research iterations completed: "
    f"{result['research_iteration_count']}"
)
    print(f"Final validation passed: {result['validation_passed']}")
    print("\nFinal validation feedback:")
    print(result["validation_feedback"])

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_query = re.sub(r"[^A-Za-z0-9]+", "_", query).strip("_")[:60]

    output_path = (
        PROJECT_ROOT
        / "outputs"
        / f"DragnetGraphReport_{safe_query}_{timestamp}.txt"
    )

    output_path.write_text(report, encoding="utf-8")

    print(f"\nReport saved to: {output_path}")


if __name__ == "__main__":
    main()