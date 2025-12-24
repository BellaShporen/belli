import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv


load_dotenv()

slack_token = os.environ.get("SLACK_BOT_TOKEN")
if not slack_token:
    raise ValueError("SLACK_BOT_TOKEN environment variable not set")

client = WebClient(token=slack_token)
channel_id = "C0A55F1911U"

def send_message_safe(channel_id, text):
    try:
        client.conversations_join(channel=channel_id)
    except SlackApiError as e:
        if e.response["error"] not in ("method_not_supported_for_channel_type", "already_in_channel"):
            print("Error joining channel:", e.response["error"])
            return
    try:
        response = client.chat_postMessage(
            channel=channel_id,
            text=text
        )
        print("Message sent successfully:", response["ts"])
    except SlackApiError as e:
        print("Error sending message:", e.response["error"])

def list_slack_channels():
    try:
        response = client.conversations_list(types="public_channel,private_channel")
        
        if response["ok"]:
            channels = response["channels"]
            print(f"Found {len(channels)} channels:")
            
            for channel in channels:
                print(f"- Name: #{channel['name']}, ID: {channel['id']}, Type: {'Private' if channel.get('is_private') else 'Public'}")
        else:
            print(f"Error fetching channels: {response['error']}")

    except SlackApiError as e:
        print(f"API Error: {e.response['error']}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    list_slack_channels()
    send_message_safe(channel_id, "שלום! זו הודעה מה-BOT שלי ")
