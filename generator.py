import os
from groq import Groq
from dotenv import load_dotenv
from voice_profile_loader import load_voice_profile, build_system_prompt

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


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
        max_tokens=1500  # increased to allow for longer LinkedIn posts
    )

    return response.choices[0].message.content