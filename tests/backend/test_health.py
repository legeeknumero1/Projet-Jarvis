"""Tests pour les endpoints de santé"""

def test_health(client):
    """Test endpoint health"""
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") in {"ok", "healthy"}
    assert "timestamp" in data


def test_metrics(client):
    """Test endpoint metrics"""
    r = client.get("/metrics")
    assert r.status_code == 200
    data = r.json()
    # Vérifier quelques métriques de base
    assert "requests_total" in str(data) or "jarvis_requests_total" in str(data)