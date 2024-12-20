import mlflow
import boto3
from datetime import datetime
import json
from tracking import track_inference # fichier dans ../mlflow/tracking.py

class ComprehendService:
    def __init__(self):
        self.comprehend = boto3.client('comprehend', region_name='eu-west-1')
        
        # Configuration MLflow
        mlflow.set_tracking_uri("http://mlflow:5000")
        mlflow.set_experiment("amazon-comprehend")
        
        self.register_comprehend_model()

    def register_comprehend_model(self):
        with mlflow.start_run(run_name="comprehend-model-registration") as run:
            mlflow.log_params({
                "model_type": "aws-comprehend",
                "version": "1.0",
                "region": "eu-west-1"
            })
            
            model_info = {
                "service": "comprehend",
                "region": "eu-west-1",
                "version": "1.0"
            }
            
            with open("model_info.json", "w") as f:
                json.dump(model_info, f)
            mlflow.log_artifact("model_info.json")
            
            mlflow.set_tag("model_type", "aws-comprehend")
            
            return run.info.run_id

    @track_inference
    def analyze_text(self, text, language='en'):
        """
        Analyse un texte avec Amazon Comprehend
        Le tracking MLflow est géré par le décorateur
        """
        sentiment = self.comprehend.detect_sentiment(
            Text=text,
            LanguageCode=language
        )
        
        entities = self.comprehend.detect_entities(
            Text=text,
            LanguageCode=language
        )
        
        key_phrases = self.comprehend.detect_key_phrases(
            Text=text,
            LanguageCode=language
        )
            
        return {
            'sentiment': {
                'sentiment': sentiment['Sentiment'],
                'scores': sentiment['SentimentScore']
            },
            'entities': [
                {
                    'text': entity['Text'],
                    'type': entity['Type'],
                    'score': entity['Score']
                }
                for entity in entities['Entities']
            ],
            'key_phrases': [
                {
                    'text': phrase['Text'],
                    'score': phrase['Score']
                }
                for phrase in key_phrases['KeyPhrases']
            ],
            'model_version': 'aws-comprehend-1.0'
        }