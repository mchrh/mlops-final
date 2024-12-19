import pytest # type: ignore
from fastapi.testclient import TestClient # type: ignore
from api.main import app # type: ignore
import io # type: ignore
from PIL import Image # type: ignore
import numpy as np # type: ignore

client = TestClient(app)

@pytest.fixture
def sample_image():
    """Crée une image test."""
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr

def test_health_check():
    """Test de l'endpoint de santé."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_detect_objects_invalid_file():
    """Test avec un fichier non-image."""
    response = client.post(
        "/detect",
        files={"file": ("test.txt", b"hello world", "text/plain")}
    )
    assert response.status_code == 400

def test_detect_objects_valid_image(sample_image):
    """Test avec une image valide."""
    response = client.post(
        "/detect",
        files={"file": ("test.png", sample_image, "image/png")},
        params={"confidence_threshold": 50.0}
    )
    assert response.status_code == 200
    assert "objects" in response.json()
    assert "inference_time" in response.json()
    assert "model_version" in response.json()

def test_confidence_threshold_validation():
    """Test de la validation du seuil de confiance."""
    response = client.post(
        "/detect",
        files={"file": ("test.png", b"invalid_image", "image/png")},
        params={"confidence_threshold": 150.0}  # Valeur invalide
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_mlflow_tracking(sample_image, mocker):
    """Test du tracking MLflow."""
    mock_mlflow = mocker.patch('mlflow.start_run')
    mock_mlflow.return_value.__enter__.return_value = mocker.Mock()
    
    response = client.post(
        "/detect",
        files={"file": ("test.png", sample_image, "image/png")}
    )
    
    assert response.status_code == 200
    mock_mlflow.assert_called_once()

def test_error_handling():
    """Test de la gestion des erreurs."""
    response = client.post("/detect")  # Pas de fichier fourni
    assert response.status_code == 422
    assert "detail" in response.json()