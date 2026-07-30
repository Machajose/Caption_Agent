import streamlit as st
from generator import generate_captions
from telegram_sender import send_telegram_message
from triage_agent import classify_and_draft
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

# --- Tabs ---
tab1, tab2 = st.tabs(["✍️ Caption Generator", "📥 Comment/DM Triage"])

# ============================================================
# TAB 1: Caption Generator
# ============================================================
with tab1:
    st.markdown("## ✍️ Caption & Post Generator")
    st.markdown('<p class="header-subtitle">Turn a rough idea into polished, on-brand content in seconds.</p>', unsafe_allow_html=True)
    st.divider()

    with st.sidebar:
        st.markdown("### Client Profiles")
        try:
            profiles_list = [f.replace(".json", "") for f in os.listdir("voice_profiles") if f.endswith(".json")]
            for p in profiles_list:
                st.markdown(f"- {p}")
        except FileNotFoundError:
            st.markdown("No profiles found yet.")

    col1, col2 = st.columns(2)
    with col1:
        try:
            profiles = [f.replace(".json", "") for f in os.listdir("voice_profiles") if f.endswith(".json")]
        except FileNotFoundError:
            profiles = []
        if profiles:
            client_name = st.selectbox("Client Profile", profiles, key="caption_client")
        else:
            client_name = st.text_input("Client Profile", placeholder="e.g. Munene", key="caption_client_text")

    with col2:
        platform = st.selectbox("Platform", ["Instagram", "LinkedIn"], key="caption_platform")

    raw_input = st.text_area(
        "Rough idea / transcript",
        height=150,
        placeholder="Paste a rough thought, voice note transcript, or update here...",
        key="caption_input"
    )

    generate_clicked = st.button("✨ Generate Options", type="primary", key="caption_generate_btn")

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

    if "captions" in st.session_state:
        st.markdown("### Generated Options")
        st.markdown(f'<div class="output-box">{st.session_state["captions"]}</div>', unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📲 Send to Telegram", key="caption_send_btn"):
                send_telegram_message(st.session_state["captions"])
                st.success("Sent to Telegram!")
        with col_b:
            st.download_button(
                "⬇️ Download as .txt",
                data=st.session_state["captions"],
                file_name=f"{client_name}_{platform.lower()}_captions.txt",
                key="caption_download_btn"
            )

# ============================================================
# TAB 2: Comment/DM Triage
# ============================================================
with tab2:
    st.markdown("## 📥 Comment/DM Triage")
    st.markdown('<p class="header-subtitle">Paste an incoming comment or DM to classify it and draft a response.</p>', unsafe_allow_html=True)
    st.divider()

    triage_client = st.selectbox("Client Profile", ["Munene", "Joseph"], key="triage_client")
    incoming_message = st.text_area("Paste the comment/DM here", height=100, key="triage_input")

    if st.button("🔍 Classify & Draft", type="primary", key="triage_classify_btn"):
        if not incoming_message:
            st.warning("Paste a message first.")
        else:
            with st.spinner("Analyzing..."):
                result = classify_and_draft(incoming_message, triage_client)
                st.session_state["triage_result"] = result

    if "triage_result" in st.session_state:
        result = st.session_state["triage_result"]
        category = result.get("category", "Unknown")

        badge_colors = {
            "FAQ": "🟢",
            "Lead": "🔵",
            "Complaint": "🔴",
            "Spam": "⚪",
            "Unknown": "🟡"
        }

        st.markdown(f"### {badge_colors.get(category, '🟡')} Category: {category}")
        st.caption(f"Confidence: {result.get('confidence', 'unknown')} — {result.get('reasoning', '')}")

        if category in ["FAQ", "Lead"] and result.get("suggested_reply"):
            st.markdown("**Suggested Reply:**")
            st.markdown(f'<div class="output-box">{result["suggested_reply"]}</div>', unsafe_allow_html=True)

            if category == "Lead":
                if st.button("📲 Send draft to Telegram for approval", key="triage_send_btn"):
                    send_telegram_message(f"New Lead detected 🔵\n\nOriginal message: {incoming_message}\n\nSuggested reply: {result['suggested_reply']}")
                    st.success("Sent to Telegram for approval!")
        elif category == "Complaint":
            st.error("⚠️ Flagged for manual review — no auto-reply drafted for complaints.")
        elif category == "Spam":
            st.info("Likely spam — no action needed.")