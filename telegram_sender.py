import os
import streamlit as st
import requests
from dotenv import load_dotenv

load_dotenv()

def get_secret(key):
    """Reads from Streamlit secrets if available, otherwise from local .env"""
    try:
        return st.secrets[key]
    except (FileNotFoundError, KeyError):
        return os.getenv(key)

BOT_TOKEN = get_secret("TELEGRAM_BOT_TOKEN")
CHAT_ID = get_secret("TELEGRAM_CHAT_ID")

def send_telegram_message(message: str) -> dict:
    """Sends a text message via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()