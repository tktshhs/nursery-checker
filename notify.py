import os
import requests


def send_message(text: str) -> None:
    """LINE Messaging API を使ってプッシュメッセージを送信する。"""
    token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    user_id = os.environ.get("LINE_USER_ID")

    if not token or not user_id:
        print("[notify] 環境変数 LINE_CHANNEL_ACCESS_TOKEN または LINE_USER_ID が未設定です。通知をスキップします。")
        return

    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    payload = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": text,
            }
        ],
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        print(f"[notify] LINE 通知を送信しました。ステータス: {response.status_code}")
    except requests.RequestException as e:
        print(f"[notify] LINE 通知の送信に失敗しました: {e}")
