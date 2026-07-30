import streamlit as st
from generator import generate_captions
from telegram_sender import send_telegram_message

st.set_page_config(page_title="Caption Generator", page_icon="✍️")

st.title("✍️ Caption / Post Generator")
st.caption("Paste a rough idea, get 3 polished options in the client's voice.")

client_name = st.text_input("Client profile name", placeholder="e.g. Joseph")
platform = st.selectbox("Platform", ["Instagram", "LinkedIn"])
raw_input = st.text_area("Rough idea / transcript", height=150, placeholder="Paste your rough thought here...")

if st.button("Generate", type="primary"):
    if not client_name or not raw_input:
        st.warning("Please fill in both fields.")
    else:
        with st.spinner("Generating..."):
            try:
                captions = generate_captions(raw_input, client_name, platform.lower())
                st.session_state["captions"] = captions
            except FileNotFoundError:
                st.error(f"No voice profile found for '{client_name}'. Check the filename in voice_profiles/.")

if "captions" in st.session_state:
    st.markdown("### Generated Options")
    st.markdown(st.session_state["captions"])

    if st.button("Send to Telegram"):
        send_telegram_message(st.session_state["captions"])
        st.success("Sent to Telegram!")