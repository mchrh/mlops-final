import pytest #type: ignore
from fastapi.testclient import TestClient #type: ignore
from api.main import app

client = TestClient(app)

@pytest.fixture
def sample_text():
    return "Amazon Comprehend is a natural language processing service that uses machine learning to discover insights from text."

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_analyze_text_empty():
    response = client.post(
        "/analyze",
        json={"text": ""}
    )
    assert response.status_code == 400

def test_analyze_text_too_long():
    response = client.post(
        "/analyze",
        json={"text": "a" * 5001}
    )
    assert response.status_code == 400

def test_analyze_text_valid(sample_text):
    response = client.post(
        "/analyze",
        json={"text": sample_text}
    )
    assert response.status_code == 200
    assert "sentiment" in response.json()
    assert "entities" in response.json()
    assert "key_phrases" in response.json()
    assert "inference_time" in response.json()

def test_analyze_text_language():
    response = client.post(
        "/analyze",
        json={"text": "Bonjour le monde", "language": "fr"}
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_mlflow_tracking(sample_text, mocker):
    mock_mlflow = mocker.patch('mlflow.start_run')
    mock_mlflow.return_value.__enter__.return_value = mocker.Mock()
    
    response = client.post(
        "/analyze",
        json={"text": sample_text}
    )
    
    assert response.status_code == 200
    mock_mlflow.assert_called_once()