from fastapi.testclient import TestClient

from lambda_function import app, configured_cors_origins


client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_analyze_csv():
    response = client.post(
        "/analyze",
        files={"file": ("ecg.csv", b"time,lead_i\n0,0.1\n1,0.2\n", "text/csv")},
    )
    assert response.status_code == 200
    assert response.json()["rows"] == 2


def test_rejects_non_csv():
    response = client.post(
        "/analyze", files={"file": ("ecg.txt", b"not csv", "text/plain")}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Please upload a CSV file."


def test_rejects_blank_csv():
    response = client.post(
        "/analyze", files={"file": ("blank.csv", b" \n\n ", "text/csv")}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "The uploaded file is not a valid CSV."


def test_allows_remote_compose_frontend_origin():
    origin = "http://ecg.example.test:3000"
    response = client.options(
        "/analyze",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin


def test_reads_configured_cors_origins(monkeypatch):
    monkeypatch.setenv(
        "CORS_ORIGINS",
        "https://ecg.example.test, https://preview.example.test ",
    )
    assert configured_cors_origins() == [
        "https://ecg.example.test",
        "https://preview.example.test",
    ]
