from unittest.mock import patch, MagicMock


MOCK_BREEDS = [
    {
        "name": "Labrador",
        "breed_group": "Sporting",
        "origin": "Canada",
        "temperament": "Friendly",
        "life_span": "10-12 years",
        "image": {"url": "https://example.com/lab.jpg"},
        "height": {"metric": "55-57"},
        "weight": {"metric": "25-36"},
    },
    {
        "name": "Poodle",
        "breed_group": "Non-Sporting",
        "origin": "Germany",
        "temperament": "Intelligent",
        "life_span": "12-15 years",
        "image": {"url": "https://example.com/poodle.jpg"},
        "height": {"metric": "38-45"},
        "weight": {"metric": "20-32"},
    },
]


def test_returns_joined_result_when_both_sources_available(client):
    """As a user, I can retrieve a consolidated resource from two sources."""
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_BREEDS * 10
    mock_response.status_code = 200

    with patch("app.requests.get", return_value=mock_response):
        with patch("app.API_KEY", "fake-key"):
            response = client.get("/dogs")

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0

    first = data[0]
    assert "breed_name" in first
    assert "image_url" in first
    assert "breed_group" in first


