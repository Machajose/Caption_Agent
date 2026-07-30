import json
import os

def load_voice_profile(client_name: str) -> dict:
    """Loads a client's voice profile JSON from the voice_profiles folder."""
    path = os.path.join("voice_profiles", f"{client_name}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"No voice profile found for '{client_name}' at {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_system_prompt(profile: dict, platform: str = "instagram") -> str:
    """Turns a voice profile dict into a system prompt for the LLM."""
    examples = "\n\n---\n\n".join(profile.get("example_posts", []))
    banned = ", ".join(profile.get("banned_words", []))

    length_instructions = {
        "instagram": "Keep each option under 150 words. Punchy, scroll-stopping, short line breaks.",
        "linkedin": "Write each option between 250-400 words. LinkedIn rewards storytelling and depth — use short paragraphs (1-3 sentences each) with line breaks for readability, but don't cut the idea short. Include a clear narrative arc: hook, context/story, insight, soft closing thought."
    }
    length_rule = length_instructions.get(platform.lower(), length_instructions["instagram"])

    system_prompt = f"""You are a social media copywriter writing exclusively in the voice of {profile['client_name']}.

CONTEXT: {profile.get('platform_notes', '')}

TONE: {profile.get('tone_description', '')}

OPENING STYLE: {profile.get('opening_style', '')}

CLOSING STYLE: {profile.get('closing_style', '')}

SENTENCE STYLE: {profile.get('sentence_length', '')}

LENGTH REQUIREMENT: {length_rule}

NEVER use these words: {banned}

Here are real examples of this client's past posts. Match this voice closely — sentence rhythm, tone, and structure:

{examples}

Your job: given a rough idea or transcript from the user, write 3 distinct caption/post options in this exact voice, following the length requirement above exactly. Number them 1, 2, 3. Do not explain your choices, just output the 3 options."""

    return system_prompt