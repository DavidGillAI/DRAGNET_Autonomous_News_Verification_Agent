from dotenv import load_dotenv
import os
import requests

# Load variables from the .env file into the Python environment.
load_dotenv()

# Read the GNews API key from the environment.
# This keeps the key out of the code and out of GitHub.
api_key = os.getenv("GNEWS_API_KEY")

# Stop early if the API key was not found.
if not api_key:
    raise ValueError("GNEWS_API_KEY not found. Check your .env file.")

# GNews search endpoint.
# This is the URL we send the request to.
url = "https://gnews.io/api/v4/search"

# Query parameters sent to GNews.
# q = search topic
# lang = English results
# max = number of articles to return
# apikey = your private API key
params = {
    "q": "UK politics",
    "lang": "en",
    "max": 5,
    "apikey": api_key,
}

# Send the request to GNews.
# timeout=10 prevents the script hanging forever if the API does not respond.
response = requests.get(url, params=params, timeout=10)

# Print the HTTP status code so we know whether the request worked.
print("Status code:", response.status_code)

# Convert the JSON response into a Python dictionary.
data = response.json()

# If GNews returns an error, print it and stop.
if response.status_code != 200:
    print("Error response:")
    print(data)
    raise SystemExit

# Get the list of articles from the response.
articles = data.get("articles", [])

print(f"Articles returned: {len(articles)}")
print()

# Print the key details for each article.
for index, article in enumerate(articles, start=1):
    print(f"Article {index}")
    print("Title:", article.get("title"))
    print("Source:", article.get("source", {}).get("name"))
    print("Published:", article.get("publishedAt"))
    print("URL:", article.get("url"))
    print("-" * 60)