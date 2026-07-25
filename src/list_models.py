from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

models = sorted(model.id for model in client.models.list().data)

for model in models:
    if model.startswith("gpt"):
        print(model)