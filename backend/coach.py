import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def ask_coach(question, history, activities_summary):
    system_prompt = (
        "You are an expert marathon running coach with deep knowledge of training periodization, "
        "recovery, and race preparation. The athlete's recent training data is below. "
        "Use it to give specific, personalized advice — reference their actual numbers, paces, "
        "and patterns when relevant. Be direct and practical.\n\n"
        f"Recent Training Data:\n{activities_summary}"
    )

    messages = []
    for msg in history:
        messages.append({"role": msg["role"], "parts": [msg["content"]]})

    messages.append({"role": "user", "parts": [question]})

    model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_prompt)
    response = model.generate_content(messages)

    return response.text
