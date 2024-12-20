from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from comprehend import ComprehendService
import mlflow
import logging
import traceback
import boto3
from prometheus_client import Counter, Histogram, Gauge, Summary, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import time

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="Text Analysis API")
comprehend_service = ComprehendService()


REQUEST_COUNT = Counter('request_count', 'Number of requests received')
ERROR_COUNT = Counter('error_count', 'Number of errors', ['error_type'])
SENTIMENT_COUNT = Counter('sentiment_count', 'Count of different sentiments detected', ['sentiment'])

ACTIVE_REQUESTS = Gauge('active_requests', 'Number of requests currently being processed')
TEXT_LENGTH = Gauge('text_length', 'Length of analyzed text')

REQUEST_LATENCY = Histogram('request_latency_seconds', 'Latency of requests')
COMPREHEND_LATENCY = Histogram('comprehend_latency_seconds', 'Latency of AWS Comprehend API calls')
SENTIMENT_CONFIDENCE = Histogram('sentiment_confidence', 'Confidence scores of sentiment analysis')

ENTITIES_PER_TEXT = Summary('entities_per_text', 'Number of entities detected per text')

@app.middleware("http")
async def add_prometheus_metrics(request, call_next):
    REQUEST_COUNT.inc()
    ACTIVE_REQUESTS.inc()
    start_time = time.time()
    
    try:
        response = await call_next(request)
        REQUEST_LATENCY.observe(time.time() - start_time)
        return response
    finally:
        ACTIVE_REQUESTS.dec()

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

class TextRequest(BaseModel):
    text: str
    language: str = 'en'

@app.post("/analyze")
async def analyze_text(request: TextRequest):
    try:
        if len(request.text.strip()) == 0:
            ERROR_COUNT.labels(error_type='400_empty_text').inc()
            raise HTTPException(400, "Text cannot be empty")
        
        if len(request.text) > 5000:
            ERROR_COUNT.labels(error_type='400_text_too_long').inc()
            raise HTTPException(400, "Text must be less than 5000 characters")
        
        TEXT_LENGTH.set(len(request.text))
        
        logger.debug("Testing AWS credentials...")
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        logger.debug(f"AWS Identity: {identity}")
        
        comprehend_start = time.time()
        logger.debug(f"Analyzing text: {request.text[:50]}...")
        result = comprehend_service.analyze_text(request.text, request.language)
        COMPREHEND_LATENCY.observe(time.time() - comprehend_start)
        
        sentiment = result['sentiment']['sentiment']
        SENTIMENT_COUNT.labels(sentiment=sentiment).inc()
        SENTIMENT_CONFIDENCE.observe(result['sentiment']['scores']['Positive'])
        
        num_entities = len(result['entities'])
        ENTITIES_PER_TEXT.observe(num_entities)
        
        logger.debug(f"Analysis result: {result}")
        
        return result
    except HTTPException as e:
        ERROR_COUNT.labels(error_type=str(e.status_code)).inc()
        logger.error(f"HTTP error in analyze_text: {str(e)}")
        raise
    except Exception as e:
        ERROR_COUNT.labels(error_type='500').inc()
        logger.error(f"Error in analyze_text: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(500, f"Internal error: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}