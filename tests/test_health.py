from unittest.mock import patch, MagicMock


def test_health_endpoint_reports_dependencies(client):
    """As an operator, /health returns OK when dependencies are reachable."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"


def test_status_endpoint_reports_database_and_api(client):
    """As an operator, /status reports the state of the database and external API."""
    mock_response = MagicMock()
    mock_response.status_code = 200

    mock_conn = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    with patch("app.get_db_connection", return_value=mock_conn):
        with patch("app.requests.get", return_value=mock_response):
            with patch("app.API_KEY", "fake-key"):
                response = client.get("/status")

    assert response.status_code == 200
    data = response.get_json()
    assert "database" in data
    assert "api" in data
    assert data["app"] == "running"