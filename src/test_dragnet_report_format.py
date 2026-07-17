from dotenv import load_dotenv
import os
import requests
from langchain_openai import ChatOpenAI


# Load API keys from .env
load_dotenv()

gnews_api_key = os.getenv("GNEWS_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

if not gnews_api_key:
    raise ValueError("GNEWS_API_KEY not found. Check your .env file.")

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found. Check your .env file.")


# Create the LLM connection.
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)


# Real news search query for DRAGNET report format test.
search_query = "Trump Balogun"


# Call GNews.
url = "https://gnews.io/api/v4/search"

params = {
    "q": search_query,
    "lang": "en",
    "max": 8,
    "apikey": gnews_api_key,
}

response = requests.get(url, params=params, timeout=10)

print("GNews status code:", response.status_code)

data = response.json()

if response.status_code != 200:
    print("GNews error response:")
    print(data)
    raise SystemExit


# Extract the article fields DRAGNET needs.
articles = []

for article in data.get("articles", []):
    articles.append(
        {
            "source": article.get("source", {}).get("name"),
            "title": article.get("title"),
            "description": article.get("description"),
            "content": article.get("content"),
            "publishedAt": article.get("publishedAt"),
            "url": article.get("url"),
        }
    )


if not articles:
    raise ValueError("No articles returned by GNews. Try a different search query.")


prompt = f"""
You are DRAGNET: Digital Research Agent Gathering News Evidence Transparently.

Your job is to produce a cautious news verification report using the provided GNews article metadata and snippets.

Important limitation:
These are not full articles. They include headlines, descriptions and partial content only.
You must not overstate certainty.

Search query:
{search_query}

Articles:
{articles}

Core rules:
- Treat every source neutrally.
- Do not assume bias based on country, outlet, or politics.
- Judge framing only from the wording and evidence in the snippets.
- Do not invent facts not present in the snippets.
- Do not treat a headline as confirmed evidence unless the article snippet supports it.
- Do not claim something is confirmed unless more than one source supports it, or the snippet cites a clear primary source.
- Treat studies, forecasts, rumours and speculation as weaker evidence unless clearly supported.
- If the articles are about mixed topics, say so.
- If evidence is too thin, say so.
- It is acceptable to conclude that the story is unresolved or needs more research.

Produce the report using exactly this format:

Story title:

Fact-Focused Summary:

Timeline, if dates matter:

Confirmed / Strongly Supported Facts:

Disputed / Unsupported / Unresolved Claims:

Overall Assessment:

Confidence Score:

Research Transparency:

What Would Clarify the Story, if inconclusive:

Sources:
"""


response = llm.invoke(prompt)

output_text = response.content

print(output_text)

# Save the DRAGNET-style report.
output_path = "outputs/dragnet_report_test_3.txt"

with open(output_path, "w", encoding="utf-8") as file:
    file.write(output_text)

print(f"\nSaved output to {output_path}")