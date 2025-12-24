import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

slack_token = os.environ.get("SLACK_BOT_TOKEN")
if not slack_token:
    raise ValueError("SLACK_BOT_TOKEN environment variable not set")

client = WebClient(token=slack_token)
channel_id = os.getenv("SLACK_CHANNEL_ID")

def send_message_safe(channel_id, text):
    try:
        client.conversations_join(channel=channel_id)
    except SlackApiError as e:
        if e.response["error"] not in ("method_not_supported_for_channel_type", "already_in_channel"):
            raise RuntimeError(f"Error joining channel: {e.response['error']}") from e
    try:
        response = client.chat_postMessage(
            channel=channel_id,
            text=text
        )
        return response["ts"]
    except SlackApiError as e:
        raise RuntimeError(f"Error sending message: {e.response['error']}") from e

def list_slack_channels():
    try:
        response = client.conversations_list(types="public_channel,private_channel")
        if response["ok"]:
            return response["channels"]
        else:
            raise RuntimeError(f"Error fetching channels: {response['error']}")
    except SlackApiError as e:
        raise RuntimeError(f"API Error: {e.response['error']}") from e
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}") from e

if __name__ == "__main__":
    channels = list_slack_channels()
    for channel in channels:
        print(f"- Name: #{channel['name']}, ID: {channel['id']}, Type: {'Private' if channel.get('is_private') else 'Public'}")
    
    ts = send_message_safe(channel_id, "Hello! This is a message from my BOT")
    print(f"Message sent successfully: {ts}")
