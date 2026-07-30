from generator import generate_captions
from telegram_sender import send_telegram_message

def run(raw_input: str, client_name: str):
    print(f"Generating captions for client: {client_name}...")
    captions = generate_captions(raw_input, client_name)

    print("\n--- Generated Options ---\n")
    print(captions)

    send = input("\nSend to Telegram? (y/n): ").strip().lower()
    if send == "y":
        send_telegram_message(captions)
        print("Sent to Telegram.")
    else:
        print("Skipped sending.")


if __name__ == "__main__":
    raw_input_text = input("Paste the rough idea / transcript: ")
    client_name = input("Client profile name (matches filename in voice_profiles/, no .json): ")
    run(raw_input_text, client_name)