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


# Create the LLM connection
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)


# Real news search query.
# Keep this fairly specific so the articles are likely to be about the same story.
search_query = "Brexit UK economy"

# Call GNews
url = "https://gnews.io/api/v4/search"

params = {
    "q": search_query,
    "lang": "en",
    "max": 5,
    "apikey": gnews_api_key,
}

response = requests.get(url, params=params, timeout=10)

print("GNews status code:", response.status_code)

data = response.json()

if response.status_code != 200:
    print("GNews error response:")
    print(data)
    raise SystemExit


# Extract the article fields we care about.
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
You are testing DRAGNET, an autonomous news research and verification agent.

You have been given real article metadata and snippets from GNews.

Important limitation:
These are not full articles. They include headlines, descriptions and partial content only.
You must not overstate certainty.

Search query:
{search_query}

Articles:
{articles}

Your task:
1. Identify the main story or stories represented by these articles.
2. Say whether the articles appear to be about the same event or mixed events.
3. Identify factual claims that appear supported by more than one source.
4. Identify claims that are disputed, unsupported, unclear, or based only on a headline.
5. Separate factual reporting from opinion, framing, or speculation.
6. Give a cautious conclusion.
7. Say whether the model passed this comparison test.

Rules:
- Do not invent facts not present in the article snippets.
- Do not assume the headline is fully supported by the article content.
- Do not claim something is confirmed unless more than one source supports it.
- If the snippets are too thin or mixed, say so clearly.
- It is acceptable to conclude that more research is needed.

Return your answer using these headings:

Main story detected:
Are the articles about the same event?:
Confirmed or strongly supported facts:
Disputed, unsupported, or unclear claims:
Source comparison:
Cautious conclusion:
Limitations:
Pass/fail assessment:
"""


response = llm.invoke(prompt)

output_text = response.content

print(output_text)

# Save the model output
output_path = "outputs/llm_real_gnews_test_2.txt"

with open(output_path, "w", encoding="utf-8") as file:
    file.write(output_text)

print(f"\nSaved output to {output_path}")