from typing import TypedDict
import re
from datetime import datetime
from urllib.parse import urlparse
from langgraph.graph import END, START, StateGraph
from src.dragnet_mvp import (
    PROJECT_ROOT,
    agent_checklist,
    build_system_prompt,
    fetch_gnews_articles,
    format_articles_for_llm,
    generate_dragnet_report,
    llm,
    client,
    OPENAI_MODEL,
    MAX_DRAFT_ITERATIONS,
    MAX_RESEARCH_ITERATIONS,
    MIN_UNIQUE_PUBLICATIONS,
)

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
    query_is_clear: bool
    query_assessment: str
    workflow_status: str
    unique_source_domains: list[str]
    source_diversity_count: int
    source_diversity_passed: bool
    web_verification_results: str

def plan_initial_search_node(state: DragnetState):
    planning_prompt = f"""
You are generating a search query for the GNews API.

Your goal is NOT to summarise the user's question.
Your goal is to maximise the chance of finding relevant news articles.

User question:
{state["query"]}

Rules:
- Return 3 to 8 keywords only.
- Keep names of people, organisations and places.
- Prefer the central event over the wording of the question.
- Replace vague phrases with the event they refer to where possible.
- Remove question words, filler words and opinions.
- Do not include punctuation or quotation marks.
- Return only the search query.

Examples:

Question:
Have UEFA lost confidence in Infantino?
Search:
UEFA FIFA Infantino boycott

Question:
Did Apple delay its AI features?
Search:
Apple AI Siri delay

Question:
Why is Grok controversial?
Search:
Grok xAI controversy

Question:
Did FIFA abandon its investment proposal?
Search:
FIFA World Cup investment proposal
""".strip()

    response = llm.invoke(planning_prompt)
    planned_query = response.content.strip()

    api_query = re.sub(r"[^\w\s-]", " ", planned_query)
    api_query = " ".join(api_query.split())

    print(f"\nUser question: {state['query']}")
    print(f"Planned search: {api_query}\n")

    return {
        "research_query": api_query,
    }

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

def web_verification_node(state: DragnetState):
    query = state["query"]

    response = client.responses.create(
        model=OPENAI_MODEL,
        tools=[{"type": "web_search_preview"}],
        input=f"""
You are verifying evidence collected from news reports.

Research the following topic:

{query}

Focus on:
- Official statements.
- Governing bodies.
- Primary sources.
- Whether key factual claims are independently corroborated.
- Whether important claims remain disputed or unsupported.

Do not simply summarise news articles.
Prioritise official and primary evidence wherever possible.

Return your findings using exactly these headings:

CONFIRMED FACTS
- Only facts supported by multiple reliable or official sources.

DISPUTED CLAIMS
- Claims where sources disagree or evidence is insufficient.

OFFICIAL SOURCES
- List any official organisations, government bodies, governing bodies or primary sources found.

KEY CONTEXT
- Important background that helps interpret the story.

REMAINING UNCERTAINTY
- What cannot currently be established.

Rules:
- Be concise.
- Do not speculate.
- Clearly distinguish evidence from inference.
- Maximum 250 words.
""",
    )

    return {
        "web_verification_results": response.output_text
    }

def assess_source_diversity_node(state: DragnetState):
    source_domains = set()

    for article in state["articles"]:
        article_url = article.get("url", "")
        domain = urlparse(article_url).netloc.lower()

        if domain.startswith("www."):
            domain = domain[4:]

        if domain:
            source_domains.add(domain)

    unique_domains = sorted(source_domains)
    diversity_count = len(unique_domains)
    diversity_passed = diversity_count >= MIN_UNIQUE_PUBLICATIONS

    print(
        f"Unique publication domains: {diversity_count} "
        f"(minimum required: {MIN_UNIQUE_PUBLICATIONS})"
    )

    updates = {
        "unique_source_domains": unique_domains,
        "source_diversity_count": diversity_count,
        "source_diversity_passed": diversity_passed,
    }

    if not diversity_passed:
        updates["validation_feedback"] = (
            f"Insufficient publication diversity. Found {diversity_count} "
            f"unique publication domains; at least "
            f"{MIN_UNIQUE_PUBLICATIONS} are required."
        )

    return updates

def decide_after_source_diversity(state: DragnetState):
    if state["source_diversity_passed"]:
        return "prepare_evidence"

    if state["research_iteration_count"] >= MAX_RESEARCH_ITERATIONS:
        return "prepare_limited_evidence"

    return "research_more"

def assess_query_node(state: DragnetState):
    article_overview = []

    for number, article in enumerate(state["articles"], start=1):
        article_overview.append(
            f"""
Article {number}
Source: {article.get("source", {}).get("name", "Unknown")}
Title: {article.get("title", "Not provided")}
Description: {article.get("description", "Not provided")}
""".strip()
        )

    assessment_prompt = f"""
Assess whether the user's query identifies one sufficiently clear news story
or claim for verification.

User query:
{state["query"]}

Retrieved article overview:
{"\n\n".join(article_overview)}

Rules:
- CLEAR means the query and results identify one main event or claim.
- AMBIGUOUS means the query is a broad topic, contains only general keywords,
  or the results describe multiple distinct stories.
- Do not invent stories or details.
- If ambiguous, provide 2 or 3 numbered clarification options based only on
  the retrieved article titles and descriptions.

Use exactly one of these on the first line:
STATUS: CLEAR
STATUS: AMBIGUOUS
""".strip()

    response = llm.invoke(assessment_prompt)
    assessment = response.content.strip()
    query_is_clear = assessment.startswith("STATUS: CLEAR")

    return {
        "query_is_clear": query_is_clear,
        "query_assessment": assessment,
        "workflow_status": (
            "researching" if query_is_clear else "needs_clarification"
        ),
    }

def decide_after_research(state: DragnetState):
    if state["research_iteration_count"] == 1:
        return "assess_query"

    return "assess_source_diversity"

def decide_after_query_assessment(state: DragnetState):
    if state["query_is_clear"]:
        return "continue_research"

    return "request_clarification"


def clarification_node(state: DragnetState):
    clarification_options = state["query_assessment"].replace(
        "STATUS: AMBIGUOUS",
        "",
    ).strip()

    clarification_message = f"""
# DRAGNET Query Clarification

The query is too broad to verify as one news story.

{clarification_options}

Please submit a more specific story or claim.
""".strip()

    return {
    "final_report": clarification_message,
    "workflow_status": "needs_clarification",
    "validation_passed": False,
    "research_iteration_count": state.get("research_iteration_count", 0),
}

def prepare_evidence_node(state: DragnetState):
    gnews_evidence = format_articles_for_llm(state["articles"])

    web_evidence = state.get("web_verification_results", "")

    evidence_package = f"""
GNEWS EVIDENCE
================
{gnews_evidence}

OPENAI WEB VERIFICATION
=======================
{web_evidence}
""".strip()

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

Publication diversity:
Unique publication domains: {state["source_diversity_count"]}
Domains found: {", ".join(state["unique_source_domains"])}
Minimum required: {MIN_UNIQUE_PUBLICATIONS}
Diversity threshold passed: {state["source_diversity_passed"]}

Use these details in Research Transparency where relevant.
Do not claim that sources are independent, unbiased, duplicated or syndicated
unless the evidence explicitly establishes that.

In Research Transparency, explicitly state:
- the unique publication-domain count;
- the minimum required count;
- whether the deterministic diversity threshold passed;
- that publication-domain diversity does not prove source independence.

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
Use PASS when every checklist requirement is satisfied.

STATUS: REVISE
Use REVISE only when one or more checklist requirements are objectively not satisfied.

After the status, explain ONLY checklist items that failed.

Do not invent new quality standards.
Do not recommend improvements unless they correspond directly to a checklist item.
If a checklist item is satisfied, treat it as passed even if it could theoretically be improved.

Verified runtime research record:
Research iterations completed: {state["research_iteration_count"]}
{research_log_text}

Publication diversity:
Unique publication domains: {state["source_diversity_count"]}
Domains found: {", ".join(state["unique_source_domains"])}
Minimum required: {MIN_UNIQUE_PUBLICATIONS}
Diversity threshold passed: {state["source_diversity_passed"]}

Use this runtime record when assessing research actions and recency.
Do not assume different publications are independent evidence chains unless
the supplied evidence establishes that.

Evidence package used for this report:
{state["evidence_package"]}

Compare the draft ONLY against:

- the supplied evidence package;
- the verified runtime record;
- the DRAGNET checklist.

Do not apply general journalism standards, legal standards,
editorial preferences or best practices unless they are explicitly required
by the checklist.

If the report satisfies a checklist item, do not fail it because you think
it could be improved.

Draft report:
{state["draft_report"]}
""".strip()

    response = llm.invoke(review_prompt)
    feedback = response.content.strip()

    llm_validation_passed = feedback.startswith("STATUS: PASS")

    validation_passed = (
        llm_validation_passed
        and state["source_diversity_passed"]
    )

    if not state["source_diversity_passed"]:
        diversity_warning = (
            "Deterministic diversity check failed: "
            f"{state['source_diversity_count']} unique publication domains found; "
            f"at least {MIN_UNIQUE_PUBLICATIONS} are required."
        )
        feedback = f"{feedback}\n\n{diversity_warning}"

    return {
        "validation_feedback": feedback,
        "validation_passed": validation_passed,
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
- If publication diversity is insufficient, target a different publication or a named primary organisation relevant to the claim.


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

Publication diversity:
Unique publication domains: {state["source_diversity_count"]}
Domains found: {", ".join(state["unique_source_domains"])}
Minimum required: {MIN_UNIQUE_PUBLICATIONS}
Diversity threshold passed: {state["source_diversity_passed"]}

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

workflow.add_node("plan_initial_search", plan_initial_search_node)
workflow.add_node("research", research_node)
workflow.add_node("web_verification", web_verification_node)
workflow.add_node("assess_source_diversity", assess_source_diversity_node,)
workflow.add_node("assess_query", assess_query_node)
workflow.add_node("request_clarification", clarification_node)
workflow.add_node("prepare_evidence", prepare_evidence_node)
workflow.add_node("generate_draft", generate_draft_node)
workflow.add_node("validate_draft", validate_draft_node)
workflow.add_node("plan_follow_up_research", plan_follow_up_research_node)
workflow.add_node("revise_draft", revise_draft_node)
workflow.add_node("finalise_report", finalise_report_node)

workflow.add_edge(START, "plan_initial_search")
workflow.add_edge("plan_initial_search", "research")
workflow.add_edge("research", "web_verification")

workflow.add_conditional_edges(
    "web_verification",
    decide_after_research,
    {
        "assess_query": "assess_query",
        "assess_source_diversity": "assess_source_diversity",
    },
)

workflow.add_conditional_edges(
    "assess_query",
    decide_after_query_assessment,
    {
        "continue_research": "assess_source_diversity",
        "request_clarification": "request_clarification",
    },
)

workflow.add_conditional_edges(
    "assess_source_diversity",
    decide_after_source_diversity,
    {
        "prepare_evidence": "prepare_evidence",
        "prepare_limited_evidence": "prepare_evidence",
        "research_more": "plan_follow_up_research",
    },
)

workflow.add_edge("request_clarification", END)

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

    if result["workflow_status"] != "needs_clarification":
        print(f"\nDraft iterations completed: {result['iteration_count']}")
        print(
            f"Research iterations completed: "
            f"{result['research_iteration_count']}"
        )
        print(
            f"Unique publication domains: "
            f"{result['source_diversity_count']}"
        )
        print(
            f"Source diversity passed: "
            f"{result['source_diversity_passed']}"
        )
        print(f"Final validation passed: {result['validation_passed']}")
        print("\nFinal validation feedback:")
        print(result["validation_feedback"])

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_query = re.sub(r"[^A-Za-z0-9]+", "_", query).strip("_")[:60]

    output_prefix = (
        "DragnetClarification"
        if result["workflow_status"] == "needs_clarification"
        else "DragnetGraphReport"
    )

    output_path = (
        PROJECT_ROOT
        / "outputs"
        / f"{output_prefix}_{safe_query}_{timestamp}.txt"
    )

    output_path.write_text(report, encoding="utf-8")

    print(f"\nReport saved to: {output_path}")


if __name__ == "__main__":
    main()