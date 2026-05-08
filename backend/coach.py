import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


def ask_coach(question, history, activities_summary):
    """Get personalized coaching advice from Claude based on training data"""
    # Initialize client with API key from environment
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Create system prompt with coach persona and athlete's activity data
    system_prompt = (
        "You are an expert marathon running coach with deep knowledge of training periodization, "
        "recovery, and race preparation. The athlete's recent training data is below. "
        "Use it to give specific, personalized advice — reference their actual numbers, paces, "
        "and patterns when relevant. Be direct and practical.\n\n"
        f"Recent Training Data:\n{activities_summary}"
    )

    # Build message history for conversation continuity
    messages = []
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    # Add current question
    messages.append({"role": "user", "content": question})

    # Call Claude with system prompt and chat history
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        system=system_prompt,
        messages=messages,
    )

    return response.content[0].text
