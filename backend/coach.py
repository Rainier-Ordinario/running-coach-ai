import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-opus-4-7"
MAX_TOKENS = 1024


def ask_coach(question, history, activities_summary):
    """Ask Claude a coaching question, grounding the answer in recent training data."""
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    system_prompt = (
        "You are an expert marathon running coach with deep knowledge of training "
        "periodization, recovery, and race preparation. The athlete's recent training "
        "data is below. Use it to give specific, personalized advice — reference "
        "their actual numbers, paces, and patterns when relevant. Be direct and practical.\n\n"
        f"Recent Training Data:\n{activities_summary}"
    )

    # Replay prior turns for conversation continuity, then append the new question.
    messages = [{"role": m["role"], "content": m["content"]} for m in history]
    messages.append({"role": "user", "content": question})

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system_prompt,
        messages=messages,
    )
    return response.content[0].text
