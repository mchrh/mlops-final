import boto3
import mlflow
from datetime import datetime

class ComprehendService:
    def __init__(self):
        self.comprehend = boto3.client('comprehend', region_name='eu-west-1')
        self.mlflow_experiment = "comprehend_nlp_analysis"
        
        try:
            self.experiment_id = mlflow.create_experiment(self.mlflow_experiment)
        except:
            self.experiment_id = mlflow.get_experiment_by_name(self.mlflow_experiment).experiment_id

    def analyze_text(self, text, language='en'):
        with mlflow.start_run():
            mlflow.log_param("language", language)
            mlflow.log_param("text_length", len(text))
            mlflow.log_param("service_version", "aws-comprehend-1.0")
            
            start_time = datetime.now()
            
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
            
            inference_time = (datetime.now() - start_time).total_seconds()
            
            mlflow.log_metric("inference_time", inference_time)
            mlflow.log_metric("sentiment_score", sentiment['SentimentScore']['Positive'])
            mlflow.log_metric("entities_count", len(entities['Entities']))
            mlflow.log_metric("key_phrases_count", len(key_phrases['KeyPhrases']))
            
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
                'inference_time': inference_time,
                'model_version': 'aws-comprehend-1.0'
            }