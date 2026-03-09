import os
import json
import pytest
from avatar_quantum_finance import app, fondos_empresa, USUARIOS_ROOT

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_login_success(client):
    region = os.getenv("REGION", "WEST")
    username = f"admin_avatar_{region}"
    password = f"QuantumSafePass2026_{region}"
    USUARIOS_ROOT[username] = password

    response = client.post('/api/auth/login', json={
        "usuario": username,
        "password": password
    })
    assert response.status_code == 200
    assert "access_token" in response.get_json()

def test_login_fail(client):
    response = client.post('/api/auth/login', json={
        "usuario": "wrong_user",
        "password": "wrong_password"
    })
    assert response.status_code == 401

def test_ver_estado_fondos_unauthorized(client):
    response = client.get('/api/finanzas/estado')
    assert response.status_code == 401

def test_privacy_analytics_logic():
    from quantum_differential_privacy import QuantumPrivateAnalytics
    qpa = QuantumPrivateAnalytics()
    data = [0.1, 0.2, 0.3]
    result = qpa.analyze_with_privacy(data)
    assert "risk_index" in result
    assert result["privacy_status"] == "Quantum Secure"
