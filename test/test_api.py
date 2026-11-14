import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_get_services(client):
    response = client.get("/api/services")

    assert response.status_code == 200
    assert isinstance(response.json, list)


def test_get_incidents(client):
    response = client.get("/api/incidents")

    assert response.status_code == 200
    assert isinstance(response.json, list)


def test_get_metrics(client):
    response = client.get("/api/metrics")

    assert response.status_code == 200
    assert "uptime" in response.json
    assert "p95_response_time" in response.json
    assert "mttr" in response.json
    assert "incident_summary" in response.json

def test_update_incident_invalid_status(client):
    response = client.patch(
        "/api/incidents/1",
        json={
            "status": "INVALID",
            "assigned_to": "Support Team"
        }
    )

    assert response.status_code == 400


def test_update_incident_empty_request(client):
    response = client.patch(
        "/api/incidents/1",
        json={}
    )

    assert response.status_code == 400

def test_add_service(client):
    response = client.post(
        "/api/services",
        json={
            "service_name": "Pytest Demo Service",
            "service_url": "https://example.org"
        }
    )

    assert response.status_code == 201
    assert response.json["message"] == "Service added successfully"

def test_add_service_missing_fields(client):
    response = client.post(
        "/api/services",
        json={}
    )

    assert response.status_code == 400