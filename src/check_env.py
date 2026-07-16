from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GNEWS_API_KEY")

if api_key:
    print("GNEWS_API_KEY loaded successfully.")
else:
    print("GNEWS_API_KEY not found.")