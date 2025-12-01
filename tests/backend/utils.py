"""Utilitaires pour les tests backend"""
import json
from typing import Dict, Any, List


def post_json(client, path: str, body: Dict[str, Any], headers: Dict[str, str] = None) -> Any:
    """Helper pour POST JSON avec gestion headers"""
    response = client.post(path, json=body, headers=headers or {})
    return response


def assert_json(response, expected_keys: List[str]):
    """Vérifie que la réponse JSON contient les clés attendues"""
    assert response.status_code == 200
    data = response.json()
    for key in expected_keys:
        assert key in data, f"Clé '{key}' manquante dans {data}"
    return data


def open_ws(client, url: str):
    """Helper pour ouvrir une connexion WebSocket"""
    return client.websocket_connect(url)


def send_chat_message(ws, message: str, user_id: str = "enzo"):
    """Helper pour envoyer un message chat via WebSocket"""
    ws.send_json({
        "message": message,
        "user_id": user_id
    })


def assert_ws_response(ws, expected_response: str = None):
    """Helper pour vérifier une réponse WebSocket"""
    data = ws.receive_json()
    assert "response" in data
    assert "timestamp" in data
    
    if expected_response:
        assert data["response"] == expected_response
    
    return data