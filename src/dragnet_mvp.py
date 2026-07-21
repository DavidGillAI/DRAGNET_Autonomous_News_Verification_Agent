import os
import re
import requests
from datetime import datetime
from langchain_openai import ChatOpenAI
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=OPENAI_API_KEY,
)

verification_rules = (PROJECT_ROOT / "reference_docs" / "verification_rules.md").read_text(
    encoding="utf-8"
)
excluded_source_rules = (
    PROJECT_ROOT / "reference_docs" / "excluded_source_rules.md"
).read_text(encoding="utf-8")
report_template = (PROJECT_ROOT / "reference_docs" / "report_template.md").read_text(
    encoding="utf-8"
)
agent_checklist = (PROJECT_ROOT / "prompts" / "agent_checklist.md").read_text(
    encoding="utf-8"
)

if not GNEWS_API_KEY:
    raise ValueError("GNEWS_API_KEY was not found in the .env file.")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY was not found in the .env file.")

def fetch_gnews_articles(search_query):
    url = "https://gnews.io/api/v4/search"

    parameters = {
        "q": search_query,
        "lang": "en",
        "max": 10,
        "apikey": GNEWS_API_KEY,
    }

    response = requests.get(url, params=parameters, timeout=20)
    response.raise_for_status()

    return response.json().get("articles", [])

def format_articles_for_llm(article_list):
    formatted_articles = []

    for number, article in enumerate(article_list, start=1):
        source_name = article.get("source", {}).get("name", "Unknown")

        formatted_articles.append(
            f"""
Article {number}
Source: {source_name}
Title: {article.get("title", "Not provided")}
Description: {article.get("description", "Not provided")}
Content: {article.get("content", "Not provided")}
Published: {article.get("publishedAt", "Not provided")}
URL: {article.get("url", "Not provided")}
""".strip()
        )

    return "\n\n".join(formatted_articles)

def build_system_prompt():
    return f"""
You are DRAGNET, an autonomous news research and verification agent.

Your job is to compare the supplied GNews article metadata and snippets
and produce a cautious, fact-focused report.

Important limits:
- The evidence comes from GNews API results.
- You may receive titles, descriptions, content snippets, publication dates,
  source names, and URLs.
- Do not pretend you have read full articles.
- Do not claim absolute truth.
- Separate confirmed or strongly supported facts from disputed, unsupported,
  unresolved, speculative, or framed claims.
- Treat studies, forecasts, rumours and economic counterfactuals as reported
  estimates unless clearly supported by primary evidence.
- In the Sources section, include the source name, article title, publication
  date, URL, and what the source was used for.
- Use the required report headings exactly as provided.
- Research Transparency must describe only limitations evident from the supplied evidence.
- Do not invent research iterations, failed tools, access dates, paywall status,
  medical evidence, or actions that were not explicitly provided.
- Do not include placeholders such as "[Access Date]".
- A URL proves where an article is located, not that the full article was accessed.
- Treat claims requiring specialist or primary evidence, including medical,
  scientific, legal, financial, and technical claims, as unconfirmed unless
  suitable supporting evidence is explicitly included in the evidence package.
- Explain the reason for the confidence score, but do not imply it is a precise
  statistical calculation.
- Before returning the report, audit every source cited, named or used anywhere,
  including the timeline. Each must have a complete Sources entry using the
  supplied metadata. If the metadata is unavailable, remove the citation or
  unsupported claim.
 - Preserve names, dates, titles and official roles exactly as supplied by the
  evidence. Do not infer or update a person's role from outside knowledge.
- Distinguish between confirming that a source reported a claim and confirming
  that the claim itself is true. Single-source, anonymous or second-hand claims
  must remain disputed, unsupported or unresolved unless corroborated or backed
  by suitable primary evidence.

Verification rules:
{verification_rules}

Excluded source rules:
{excluded_source_rules}

Agent checklist:
{agent_checklist}

Required report format:
{report_template}
""".strip()

def generate_dragnet_report(search_query, evidence):
    prompt = f"""
{build_system_prompt()}

User search query:
{search_query}

GNews evidence package:
{evidence}
""".strip()

    response = llm.invoke(prompt)

    return response.content

def main():
    print("DRAGNET environment loaded successfully.")

    query = input("Enter a news story or search query: ").strip()

    if not query:
        raise ValueError("A news query is required.")

    print(f"Researching: {query}")

    articles = fetch_gnews_articles(query)

    if not articles:
        raise ValueError("GNews returned no articles for this query.")

    print(f"Found {len(articles)} articles.")

    evidence_package = format_articles_for_llm(articles)

    print(f"Evidence package prepared: {len(evidence_package)} characters.")
    print("\nPreview:\n")
    print(evidence_package[:1000])
    print("\nGenerating DRAGNET report...")

    report = generate_dragnet_report(query, evidence_package)

    print("\nDRAGNET REPORT\n")
    print(report)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_query = re.sub(r"[^A-Za-z0-9]+", "_", query).strip("_")[:60]

    output_path = (
        PROJECT_ROOT
        / "outputs"
        / f"DragnetReport_{safe_query}_{timestamp}.txt"
    )

    output_path.write_text(report, encoding="utf-8")

    print(f"\nReport saved to: {output_path}")


if __name__ == "__main__":
    main()