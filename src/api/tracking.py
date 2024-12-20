import mlflow
from functools import wraps
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_mlflow(tracking_uri=None, experiment_name="rekognition_object_detection"):
    """Initialise MLflow avec l'URI de tracking et l'expérience spécifiés."""
    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)
    
    try:
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            experiment_id = mlflow.create_experiment(experiment_name)
        else:
            experiment_id = experiment.experiment_id
        mlflow.set_experiment(experiment_name)
        return experiment_id
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de MLflow: {str(e)}")
        raise

def track_inference(func):
    """Décorateur pour tracker automatiquement les inférences avec MLflow."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        with mlflow.start_run(nested=True):
            params = {
                'confidence_threshold': kwargs.get('confidence_threshold', 50.0),
                'service_version': 'aws-rekognition-1.0',
                'timestamp': datetime.now().isoformat()
            }
            mlflow.log_params(params)
            
            start_time = datetime.now()
            result = func(*args, **kwargs)
            inference_time = (datetime.now() - start_time).total_seconds()
            
            metrics = {
                'inference_time': inference_time,
                'number_of_objects': len(result.get('objects', [])),
                'average_confidence': sum(obj['confidence'] for obj in result.get('objects', [])) / len(result.get('objects', [])) if result.get('objects') else 0
            }
            mlflow.log_metrics(metrics)
            
            tags = {
                'environment': 'production',
                'service': 'rekognition',
                'api_version': '1.0'
            }
            mlflow.set_tags(tags)
            
            return result
    return wrapper

def log_model_metadata(model_info):
    with mlflow.start_run():
        mlflow.log_params({
            'model_name': 'amazon-rekognition',
            'model_version': model_info.get('version', 'unknown'),
            'last_updated': datetime.now().isoformat()
        })