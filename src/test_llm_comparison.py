from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI


# Load API keys from .env
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found. Add it to your .env file.")


# Create the LLM connection.
# We start with the smaller model so we can test whether it is strong enough.
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)


# Controlled test case:
# The articles are deliberately written so one source makes a stronger claim
# than the others can support.
articles = [
    {
        "source": "Outlet A",
        "title": "Police investigate city centre incident",
        "content": (
            "Police said no arrests have been made after an incident in the city centre "
            "on Monday evening. Officers said the investigation is ongoing and appealed "
            "for witnesses."
        ),
    },
    {
        "source": "Outlet B",
        "title": "Man arrested after city centre incident",
        "content": (
            "A local report claimed that a man was arrested after the city centre incident. "
            "The article did not cite police confirmation or name an official source for "
            "the arrest claim."
        ),
    },
    {
        "source": "Outlet C",
        "title": "Investigation continues after city centre incident",
        "content": (
            "Officials said the investigation remains ongoing after Monday's city centre "
            "incident. They asked anyone with information to contact police."
        ),
    },
]


prompt = f"""
You are testing a news verification agent.

Compare the following article summaries about the same story.

Your task:
1. Identify the factual claims.
2. Say which claims are confirmed by multiple sources.
3. Say which claims are disputed, unsupported, or unclear.
4. Separate confirmed facts from stronger claims that are not fully supported.
5. Give a cautious final conclusion.

Important rules:
- Do not assume a claim is true just because one source states it.
- Do not treat a headline as stronger evidence than the article content.
- If sources conflict, clearly say so.
- It is acceptable to conclude that something is unclear.

Articles:
{articles}

Return your answer using these headings:

Confirmed facts:
Disputed or unsupported claims:
Source comparison:
Cautious conclusion:
Pass/fail assessment of the model's reasoning:
"""


response = llm.invoke(prompt)

# Store the model's answer in a variable so we can print it and save it.
output_text = response.content

# Print the result in the terminal.
print(output_text)

# Save the result as a text file in the outputs folder.
with open("outputs/llm_comparison_test_1.txt", "w", encoding="utf-8") as file:
    file.write(output_text)

print("\nSaved output to outputs/llm_comparison_test_1.txt")