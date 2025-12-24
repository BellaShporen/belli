import os
os.environ["SLACK_BOT_TOKEN"] = "fake-token"
import pytest
from unittest.mock import MagicMock, patch
import slack_connections
from slack_sdk.errors import SlackApiError


@pytest.fixture
def mock_client():
    with patch('slack_connections.client') as mock:
        yield mock

def test_send_message_safe_success(mock_client):
    mock_client.conversations_join.return_value = {}
    mock_client.chat_postMessage.return_value = {"ts": "12345.6789"}
    ts = slack_connections.send_message_safe("C0A55F1911U", "Hello")
    mock_client.conversations_join.assert_called_once_with(channel="C0A55F1911U")
    mock_client.chat_postMessage.assert_called_once_with(channel="C0A55F1911U", text="Hello")
    assert ts == "12345.6789"

def test_send_message_safe_join_error_allowed(mock_client):
    mock_client.conversations_join.side_effect = SlackApiError(
        message="error",
        response={"error": "already_in_channel"}
    )
    mock_client.chat_postMessage.return_value = {"ts": "12345.6789"}
    ts = slack_connections.send_message_safe("C0A55F1911U", "Hello")
    mock_client.chat_postMessage.assert_called_once()
    assert ts == "12345.6789"

def test_send_message_safe_join_error_not_allowed(mock_client):
    mock_client.conversations_join.side_effect = SlackApiError(
        message="error",
        response=MagicMock(data={"error": "some_other_error"})
    )

    with pytest.raises(RuntimeError, match="Error joining channel"):
        slack_connections.send_message_safe("C0A55F1911U", "Hello")
    
    mock_client.chat_postMessage.assert_not_called()

def test_list_slack_channels_success(mock_client):
    mock_client.conversations_list.return_value = {
        "ok": True,
        "channels": [
            {"name": "social", "id": "C123", "is_private": False},
            {"name": "all-b-slack", "id": "C124", "is_private": False},
        ]
    }

    channels = slack_connections.list_slack_channels()
    mock_client.conversations_list.assert_called_once_with(types="public_channel,private_channel")
    assert len(channels) == 2
    assert channels[0]["name"] == "social"

def test_list_slack_channels_api_error(mock_client):
    mock_client.conversations_list.side_effect = SlackApiError(
        message="error",
        response=MagicMock(data={"error": "api_error"})
    )

    with pytest.raises(RuntimeError, match="API Error:"):
        slack_connections.list_slack_channels()
    
    mock_client.conversations_list.assert_called_once()
