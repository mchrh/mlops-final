import boto3 # type: ignore
import mlflow
from datetime import datetime

class RekognitionService:
    def __init__(self):
        self.rekognition = boto3.client('rekognition')
        self.mlflow_experiment = "rekognition_object_detection"
        
        try:
            self.experiment_id = mlflow.create_experiment(self.mlflow_experiment)
        except:
            self.experiment_id = mlflow.get_experiment_by_name(self.mlflow_experiment).experiment_id

    def detect_objects(self, image_bytes, confidence_threshold=50):
        with mlflow.start_run():
            # logging params
            mlflow.log_param("confidence_threshold", confidence_threshold)
            mlflow.log_param("service_version", "aws-rekognition-1.0")
            
            start_time = datetime.now()
            
            response = self.rekognition.detect_labels(
                Image={'Bytes': image_bytes},
                MinConfidence=confidence_threshold
            )
            
            # calc tps d'inférence
            inference_time = (datetime.now() - start_time).total_seconds()
            
            # logging metrics
            mlflow.log_metric("inference_time", inference_time)
            mlflow.log_metric("number_of_objects", len(response['Labels']))
            
            objects = [
                {
                    'name': label['Name'],
                    'confidence': label['Confidence'],
                    'parents': [parent['Name'] for parent in label.get('Parents', [])]
                }
                for label in response['Labels']
            ]
            
            return {
                'objects': objects,
                'inference_time': inference_time,
                'model_version': 'aws-rekognition-1.0'
            }