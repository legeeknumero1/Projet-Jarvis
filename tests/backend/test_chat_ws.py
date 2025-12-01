"""Tests pour WebSocket chat"""

def test_ws_roundtrip(client):
    """Test WebSocket roundtrip simple"""
    with client.websocket_connect("/ws") as websocket:
        # Envoyer message
        websocket.send_json({"message": "ping", "user_id": "enzo"})
        
        # Recevoir réponse
        data = websocket.receive_json()
        assert "response" in data or "answer" in data
        response_text = data.get("response", data.get("answer", ""))
        assert response_text.startswith("ACK::")
        assert "enzo" in str(data)


def test_ws_multiple_messages(client):
    """Test WebSocket multiple messages dans même connexion"""
    with client.websocket_connect("/ws") as websocket:
        messages = ["hello", "comment ça va", "au revoir"]
        
        for msg in messages:
            websocket.send_json({"message": msg, "user_id": "enzo"})
            data = websocket.receive_json()
            response_text = data.get("response", data.get("answer", ""))
            assert f"ACK::{msg}" in response_text