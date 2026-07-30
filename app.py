import streamlit as st
from generator import generate_captions
from telegram_sender import send_telegram_message
import os

st.set_page_config(
    page_title="Caption Generator",
    page_icon="✍️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Custom styling ---
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        padding: 0.6rem 0;
        font-weight: 600;
        border: none;
    }
    .stButton>button[kind="primary"] {
        background-color: #6C5CE7;
        color: white;
    }
    .stButton>button[kind="primary"]:hover {
        background-color: #5849c2;
    }
    .output-box {
        background-color: #1e1e2f;
        border: 1px solid #333;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
        white-space: pre-wrap;
        line-height: 1.6;
    }
    .header-subtitle {
        color: #999;
        font-size: 0.95rem;
        margin-top: -0.5rem;
    }
    div[data-testid="stTextArea"] textarea {
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("## ✍️ Caption & Post Generator")
st.markdown('<p class="header-subtitle">Turn a rough idea into polished, on-brand content in seconds.</p>', unsafe_allow_html=True)
st.divider()

# --- Sidebar: available client profiles ---
with st.sidebar:
    st.markdown("### Client Profiles")
    try:
        profiles = [f.replace(".json", "") for f in os.listdir("voice_profiles") if f.endswith(".json")]
        for p in profiles:
            st.markdown(f"- {p}")
    except FileNotFoundError:
        st.markdown("No profiles found yet.")

# --- Input section ---
col1, col2 = st.columns(2)
with col1:
    try:
        profiles = [f.replace(".json", "") for f in os.listdir("voice_profiles") if f.endswith(".json")]
    except FileNotFoundError:
        profiles = []
    if profiles:
        client_name = st.selectbox("Client Profile", profiles)
    else:
        client_name = st.text_input("Client Profile", placeholder="e.g. Munene")

with col2:
    platform = st.selectbox("Platform", ["Instagram", "LinkedIn"])

raw_input = st.text_area(
    "Rough idea / transcript",
    height=150,
    placeholder="Paste a rough thought, voice note transcript, or update here..."
)

generate_clicked = st.button("✨ Generate Options", type="primary")

# --- Generation ---
if generate_clicked:
    if not client_name or not raw_input:
        st.warning("Please select a client profile and enter an idea.")
    else:
        with st.spinner("Writing in their voice..."):
            try:
                captions = generate_captions(raw_input, client_name, platform.lower())
                st.session_state["captions"] = captions
            except FileNotFoundError:
                st.error(f"No voice profile found for '{client_name}'.")

# --- Output section ---
if "captions" in st.session_state:
    st.markdown("### Generated Options")
    st.markdown(f'<div class="output-box">{st.session_state["captions"]}</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("📲 Send to Telegram"):
            send_telegram_message(st.session_state["captions"])
            st.success("Sent to Telegram!")
    with col_b:
        st.download_button(
            "⬇️ Download as .txt",
            data=st.session_state["captions"],
            file_name=f"{client_name}_{platform.lower()}_captions.txt"
        )