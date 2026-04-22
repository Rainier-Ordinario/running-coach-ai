import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def ask_coach(question, history, activities_summary):
    """Get personalized coaching advice from Gemini based on training data"""
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
        messages.append({"role": msg["role"], "parts": [msg["content"]]})

    # Add current question
    messages.append({"role": "user", "parts": [question]})

    # Call Gemini with system prompt and chat history
    model = genai.GenerativeModel("gemini-2.0-flash", system_instruction=system_prompt)
    response = model.generate_content(messages)

    return response.text
