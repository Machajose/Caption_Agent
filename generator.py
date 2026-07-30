import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from voice_profile_loader import load_voice_profile, build_system_prompt

load_dotenv()

def get_api_key():
    """Reads GROQ_API_KEY from Streamlit secrets if available, otherwise from local .env"""
    try:
        return st.secrets["GROQ_API_KEY"]
    except (FileNotFoundError, KeyError):
        return os.getenv("GROQ_API_KEY")

client = Groq(api_key=get_api_key())


def generate_captions(raw_input: str, client_name: str, platform: str = "instagram") -> str:
    """Generates 3 caption/post variants matching a client's voice profile."""
    profile = load_voice_profile(client_name)
    system_prompt = build_system_prompt(profile, platform)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": raw_input}
        ],
        temperature=0.8,
        max_tokens=1500
    )

    return response.choices[0].message.content

