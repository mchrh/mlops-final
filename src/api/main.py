from fastapi import FastAPI, File, UploadFile, HTTPException
from rekognition import RekognitionService
import mlflow

app = FastAPI(title="Object Detection API")
rekognition_service = RekognitionService()

@app.post("/detect")
async def detect_objects(
    file: UploadFile = File(...),
    confidence_threshold: float = 50.0
):
    if not file.content_type.startswith('image/'):
        raise HTTPException(400, "File must be an image")
    
    contents = await file.read()
    return rekognition_service.detect_objects(contents, confidence_threshold)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}