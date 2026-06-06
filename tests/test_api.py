from fastapi.testclient import TestClient

from app.main import app


def test_root():

    with TestClient(app) as client:

        response = client.get("/")

        assert response.status_code == 200

        data = response.json()

        assert data["status"] == "running"


def test_analysis_endpoint():

    with TestClient(app) as client:

        response = client.get(
            "/analysis/top-crimes",
            params={
                "city": "Kolkata"
            }
        )

        assert response.status_code == 200


def test_query_endpoint():

    with TestClient(app) as client:

        response = client.post(
            "/query/",
            json={
                "query":
                    "Show theft trend in Kolkata"
            }
        )

        assert response.status_code == 200