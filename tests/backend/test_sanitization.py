"""Tests pour la sanitisation XSS"""

def test_xss_script_rejected(client):
    """Test que les scripts sont rejetés"""
    payload = {"message": "<script>alert(1)</script>", "user_id": "enzo"}
    r = client.post("/chat/", json=payload)
    assert r.status_code in (400, 422), f"Expected 400/422, got {r.status_code}: {r.text}"


def test_xss_javascript_rejected(client):
    """Test que javascript: est rejeté"""
    payload = {"message": "javascript:alert('xss')", "user_id": "enzo"}
    r = client.post("/chat/", json=payload)
    assert r.status_code in (400, 422)


def test_html_entities_sanitized(client):
    """Test que les entités HTML basiques passent mais sont échappées"""
    # Le message doit passer la validation mais être sanitisé
    payload = {"message": "Hello <b>world</b>", "user_id": "enzo"}
    r = client.post("/chat/", json=payload)
    
    # Si ça passe (200), vérifier que la réponse est sanitisée
    if r.status_code == 200:
        data = r.json()
        # La réponse ne doit pas contenir de HTML brut
        assert "<b>" not in data["response"]
        assert "&lt;b&gt;" in data["response"] or "ACK::Hello &lt;b&gt;world&lt;/b&gt;" in data["response"]
    else:
        # Si ça ne passe pas, c'est aussi acceptable (validation stricte)
        assert r.status_code in (400, 422)


def test_safe_message_passes(client):
    """Test qu'un message safe passe normalement"""
    payload = {"message": "Bonjour Jarvis, comment ça va ?", "user_id": "enzo"}
    r = client.post("/chat/", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["response"] == "ACK::Bonjour Jarvis, comment ça va ?"