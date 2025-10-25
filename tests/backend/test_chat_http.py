"""Tests pour les endpoints chat HTTP"""

def test_chat_public(client):
    """Test chat endpoint public"""
    payload = {"message": "salut", "user_id": "enzo"}
    r = client.post("/chat/", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["response"] == "ACK::salut"
    assert data["user_id"] == "enzo"
    assert data["memory_saved"] is True


def test_chat_secure_no_auth(client):
    """Test chat secure sans authentification - doit échouer"""
    payload = {"message": "yo", "user_id": "enzo"}
    r = client.post("/chat/secure", json=payload)
    assert r.status_code == 401


def test_chat_secure_with_auth(client, auth_headers):
    """Test chat secure avec authentification valide"""
    payload = {"message": "yo", "user_id": "enzo"}
    r = client.post("/chat/secure", json=payload, headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["response"] == "ACK::yo"


def test_chat_empty_message(client):
    """Test chat avec message vide - doit être rejeté"""
    payload = {"message": "", "user_id": "enzo"}
    r = client.post("/chat/", json=payload)
    assert r.status_code in (400, 422)  # Erreur validation Pydantic


def test_chat_long_message(client):
    """Test chat avec message trop long - doit être rejeté"""
    long_message = "a" * 6000  # > 5000 caractères
    payload = {"message": long_message, "user_id": "enzo"}
    r = client.post("/chat/", json=payload)
    assert r.status_code in (400, 422)  # Erreur validation Pydantic