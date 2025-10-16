import json


def test_websocket_chat(client):
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_text(json.dumps({"message": "Hello", "user_id": "ws-user"}))

        messages = []
        for _ in range(10):
            try:
                data = ws.receive_text(timeout=2)
                payload = json.loads(data)
                messages.append(payload)
                if payload.get("type") == "complete":
                    break
            except Exception:
                break

        types = [m.get("type") for m in messages]
        assert "processing" in types
        assert "chunk" in types
        assert "complete" in types


