import json
from generator import client  # reuses the Groq client already set up in generator.py


def load_faq_bank(client_name: str) -> dict:
    path = f"faq_bank/{client_name}.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"business_context": "", "faqs": []}


def classify_and_draft(message_text: str, client_name: str) -> dict:
    """
    Classifies an incoming comment/DM and drafts a reply if appropriate.
    Returns a dict with: category, confidence, suggested_reply, reasoning
    """
    faq_data = load_faq_bank(client_name)
    faq_text = "\n".join([f"- {f['topic']}: {f['answer']}" for f in faq_data.get("faqs", [])])

    system_prompt = f"""You are a triage assistant for {client_name}'s Instagram/LinkedIn inbox.

BUSINESS CONTEXT: {faq_data.get('business_context', '')}

KNOWN FAQ ANSWERS (use these exact answers when the message matches one of these topics):
{faq_text}

Your job: read the incoming message and classify it into exactly one category:
- "FAQ": matches one of the known FAQ topics above
- "Lead": genuine interest but NOT a simple FAQ match (needs a personalized, thoughtful reply)
- "Complaint": negative, frustrated, or critical message
- "Spam": bot-like, irrelevant, or promotional junk

Then respond ONLY in this exact JSON format, nothing else, no markdown fences:
{{
  "category": "FAQ" | "Lead" | "Complaint" | "Spam",
  "confidence": "high" | "medium" | "low",
  "suggested_reply": "a natural, human-sounding reply, or empty string if category is Complaint or Spam",
  "reasoning": "one short sentence explaining the classification"
}}

For Complaint and Spam categories, suggested_reply must be an empty string — these should never get an auto-reply, only a flag for human review."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message_text}
        ],
        temperature=0.4,
        max_tokens=500
    )

    raw_output = response.choices[0].message.content.strip()

    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        return {
            "category": "Unknown",
            "confidence": "low",
            "suggested_reply": "",
            "reasoning": "Could not parse model output — review manually."
        }