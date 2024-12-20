from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from comprehend import ComprehendService
import mlflow
import logging
import traceback
import boto3

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="Text Analysis API")
comprehend_service = ComprehendService()

class TextRequest(BaseModel):
    text: str
    language: str = 'en'

@app.post("/analyze")
async def analyze_text(request: TextRequest):
    try:
        if len(request.text.strip()) == 0:
            raise HTTPException(400, "Text cannot be empty")
        
        if len(request.text) > 5000:
            raise HTTPException(400, "Text must be less than 5000 characters")
        
        logger.debug("Testing AWS credentials...")
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        logger.debug(f"AWS Identity: {identity}")
        
        logger.debug(f"Analyzing text: {request.text[:50]}...")
        result = comprehend_service.analyze_text(request.text, request.language)
        logger.debug(f"Analysis result: {result}")
        
        return result
    except Exception as e:
        logger.error(f"Error in analyze_text: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(500, f"Internal error: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}