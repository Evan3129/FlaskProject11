from unittest.mock import patch
import requests as req


def test_graceful_degradation_on_upstream_failure(client):
    """As a user, if the external API is down, I get a meaningful error or cached data."""
    with patch("app.requests.get", side_effect=req.RequestException("API unavailable")):
        with patch("app.API_KEY", "fake-key"):
            response = client.get("/dogs")

    assert response.status_code in [200, 500, 503]
    data = response.get_json()
    assert data is not None

    # Should return a meaningful error message, not crash silently
    if response.status_code != 200:
        assert "error" in data