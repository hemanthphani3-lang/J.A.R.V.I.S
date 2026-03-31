import webbrowser
import os
import requests
import time
import pyautogui

class Communications:
    def __init__(self, telegram_token=None, auth_id=None):
        self.telegram_token = telegram_token
        self.auth_id = auth_id

    def send_whatsapp(self, phone, message):
        """Open WhatsApp Web for message sending."""
        try:
            # Clean phone number (remove +, spaces, etc)
            clean_phone = "".join(e for e in str(phone) if e.isdigit())
            from urllib.parse import quote
            url = f"https://web.whatsapp.com/send?phone={clean_phone}&text={quote(message)}"
            webbrowser.open(url)
            # We don't force 'Enter' by default for safety, but can be added if requested.
            return f"WhatsApp protocol initiated for {phone}. Interface active."
        except Exception as e:
            return f"WhatsApp Error: {str(e)}"

    def send_telegram(self, message, chat_id=None):
        """Send a telegram message via JARVIS bot."""
        if not self.telegram_token:
            return "Telegram Token not initialized, Sir."
        
        target_id = chat_id or self.auth_id
        if not target_id:
            return "No authorized user ID for transmission, Sir."
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {"chat_id": target_id, "text": message}
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                return "Telegram packet transmitted successfully."
            return f"Telegram Transmission Failure: {response.text}"
        except Exception as e:
            return f"Telegram Error: {str(e)}"

# Unified logic function
def communication_logic(platform, target, message):
    comm = Communications(
        telegram_token=os.getenv("TELEGRAM_TOKEN"),
        auth_id=os.getenv("AUTHORIZED_USER_ID")
    )
    if "whatsapp" in platform.lower():
        return comm.send_whatsapp(target, message)
    if "telegram" in platform.lower():
        return comm.send_telegram(message, target)
    return f"Communication protocol {platform} not identified."
