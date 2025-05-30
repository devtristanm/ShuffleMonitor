from telethon import TelegramClient, events
import re
import requests

# Telegram credentials
api_id = 21883425
api_hash = '7d81e73958ea212c65f113f3bfe7e761'

# Discord webhook info
discord_webhook_url = "https://discord.com/api/webhooks/1377196939753558066/yG5ldn5blEhQOBjtqDw6P_aWfnDKtdDkzJ6YRKBObs2Eee2T5aDFSENp6CrWP7SAMnzu"
role_id = "1377197036218093668"

# Channels
channels_to_monitor = [
    -1001517758091,  # Wings of Horus
    -1001653331942,  # VIP Drop
    -1001610623118   # Boost Alert
]

# Telegram client
client = TelegramClient('session_name', api_id, api_hash)

@client.on(events.NewMessage(chats=channels_to_monitor))
async def handler(event):
    message_text = event.message.message
    chat_id = event.chat_id

    # Strip and split by non-empty lines
    lines = [line.strip() for line in message_text.splitlines() if line.strip()]

    code = None
    value = None
    wager_requirement = None
    reward_line = None

    try:
        if chat_id == -1001517758091:
            # Wings of Horus
            for i, line in enumerate(lines):
                if "Code to get you started" in line:
                    code = lines[i + 1].strip() if i + 1 < len(lines) else None
                    reward_line = lines[i + 2].strip() if i + 2 < len(lines) else None
                    break
        elif chat_id == -1001653331942 and lines[0].startswith("VIP Drop"):
            # VIP Drop
            code = lines[1] if len(lines) > 1 else None
            reward_line = lines[2] if len(lines) > 2 else None
        elif chat_id == -1001610623118 and lines[0].startswith("Boost Alert"):
            # Boost Alert
            code = lines[1] if len(lines) > 1 else None
            reward_line = lines[2] if len(lines) > 2 else None

        # Parse reward and wager if we got a reward_line
        if reward_line:
            match = re.search(r"\$(\d+(?:\.\d+)?)\s+for the first.*?-\s+\$?([\d,]+)", reward_line)
            if match:
                value = match.group(1)
                wager_requirement = match.group(2)

        if code and value and wager_requirement:
            content = (
                f"**New Promo Code Alert!**\n\n"
                f"🔹 **Code:** `{code}`\n"
                f"💰 **Value:** ${value}\n"
                f"📈 **Wager Requirement:** ${wager_requirement}\n\n"

                f"<@&{role_id}>\n"
            )
            data = {"content": content}
            response = requests.post(discord_webhook_url, json=data)
            if response.status_code != 204:
                print(f"Webhook failed: {response.status_code} - {response.text}")
        else:
            print("Message skipped — missing required data:")
            print(message_text)
    except Exception as e:
        print(f"Error processing message: {e}")
        print(message_text)

# Start
print("Starting Telegram client...")
client.start()
print("Client is running and monitoring channels.")
client.run_until_disconnected()
