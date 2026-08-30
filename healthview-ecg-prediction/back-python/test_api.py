from fastapi.testclient import TestClient

from lambda_function import app


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
