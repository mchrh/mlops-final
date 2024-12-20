# MLOps Project Documentation

## Architecture et Choix Techniques

### Vue d'ensemble
Ce projet implémente une chaîne MLOps complète intégrant l'ensemble des pratiques DevOps et les outils spécifiques au Machine Learning, utilisant une approche Infrastructure as Code (IaC).

### Infrastructure
- **Cloud Provider** : AWS (région eu-west-1)
- **Infrastructure as Code** : Terraform pour la gestion de l'infrastructure
- **Conteneurisation** : Docker et Docker Compose
- **CI/CD** : GitHub Actions

### Stack Technique
1. **Application ML**
   - API basée sur FastAPI
   - Utilisation d'Amazon Comprehend pour l'analyse de sentiment
   - MLflow pour le tracking des expériences et le versioning des modèles
   - Prometheus pour la collecte de métriques
   - Grafana pour la visualisation

2. **Monitoring**
   - Prometheus pour la collecte des métriques
   - Grafana pour la visualisation
   - Métriques personnalisées pour le suivi des performances ML

3. **Stockage**
   - S3 pour les artifacts MLflow
   - SQLite pour le backend MLflow

## Guide d'Installation Pas à Pas

### Prérequis
- AWS CLI configuré
- Terraform installé
- Docker et Docker Compose installés
- Clé SSH pour AWS EC2

### 1. Configuration AWS
```bash
# Configurer AWS CLI
aws configure
# Entrer vos credentials AWS et la région eu-west-1
```

### 2. Déploiement de l'Infrastructure
```bash
# Cloner le repository
git clone [URL_DU_REPO]
cd [NOM_DU_PROJET]

# Initialiser et appliquer Terraform
cd infrastructure/terraform
terraform init
terraform apply
```

### 3. Configuration des Services
```bash
# Se connecter à l'instance EC2
ssh -i ~/.ssh/mlops-key.pem ubuntu@<EC2_IP>

# Déployer les services
cd /home/ubuntu
docker-compose up -d
```

### 4. Vérification du Déploiement
- MLflow UI : http://<EC2_IP>:5000
- API : http://<EC2_IP>:8000
- Prometheus : http://<EC2_IP>:9090
- Grafana : http://<EC2_IP>:3000

## Documentation des APIs
![alt text](<Screenshot 2024-12-20 at 16.01.58.png>)
### API Principale

#### Health Check
```http
GET /health
```
Retourne le statut de l'API.

**Réponse** :
```json
{
    "status": "healthy"
}
```

#### Analyse de Texte
```http
POST /analyze
```
Analyse un texte donné en utilisant Amazon Comprehend.

**Corps de la requête** :
```json
{
    "text": "Your text to analyze",
    "language": "en"  // Optional, default: "en"
}
```

**Réponse** :
```json
{
    "sentiment": {
        "sentiment": "POSITIVE",
        "scores": {
            "Positive": 0.99,
            "Negative": 0.01,
            "Neutral": 0.00,
            "Mixed": 0.00
        }
    },
    "entities": [
        {
            "text": "AWS",
            "type": "ORGANIZATION",
            "score": 0.98
        }
    ],
    "key_phrases": [
        {
            "text": "great service",
            "score": 0.99
        }
    ],
    "model_version": "aws-comprehend-1.0"
}
```

#### Métriques
```http
GET /metrics
```
Expose les métriques Prometheus.
![alt text](<Screenshot 2024-12-20 at 18.45.31.png>)

### Métriques Disponibles
- `request_count` : Nombre total de requêtes
- `request_latency_seconds` : Latence des requêtes
- `error_count` : Nombre d'erreurs par type
- `sentiment_count` : Comptage des sentiments détectés
- `active_requests` : Nombre de requêtes actives
- `text_length` : Longueur des textes analysés
- `comprehend_latency_seconds` : Latence des appels à AWS Comprehend
- `sentiment_confidence` : Scores de confiance des analyses
- `entities_per_text` : Nombre d'entités détectées par texte

![alt text](<Screenshot 2024-12-20 at 16.01.58.png>)

## Sécurité
- IAM roles pour l'accès aux services AWS
- Security groups configurés pour limiter l'accès
- HTTPS recommandé pour la production

## Maintenance
Pour mettre à jour l'application :
```bash
git pull
docker-compose build
docker-compose up -d
```

Pour les logs :
```bash
docker-compose logs -f
```

Pour nettoyer l'infrastructure :
```bash
terraform destroy
```

## Déploiement Automatique avec GitHub Actions

### 1. Préparation du Repository
```bash
# Sur votre machine locale
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <votre-repo-github>
git push -u origin main
```

### 2. Configuration des Secrets GitHub
Dans votre repository GitHub, allez dans Settings > Secrets and variables > Actions et ajoutez ces secrets :

- `AWS_ACCESS_KEY_ID` : Votre Access Key ID AWS
- `AWS_SECRET_ACCESS_KEY` : Votre Secret Access Key AWS
- `EC2_SSH_KEY` : Votre clé SSH privée en base64
  ```bash
  # Pour convertir votre clé en base64
  cat ~/.ssh/mlops-key.pem | base64
  ```

### 3. Structure des Fichiers pour le Déploiement
```
.github/
└── workflows/
    └── deploy.yml    # Configuration du workflow
```

### 4. Déploiement
Le déploiement se fait automatiquement à chaque push sur la branche main. Pour déclencher un déploiement :
```bash
# Après avoir fait des modifications
git add .
git commit -m "Update application"
git push origin main
```

### 5. Suivi du Déploiement
- Allez dans l'onglet "Actions" de votre repository GitHub
- Vous verrez le workflow "Deploy MLOps Application" en cours d'exécution
- Cliquez sur le workflow pour voir les détails et les logs

### 6. Vérification du Déploiement
Après un déploiement réussi, vérifiez que les services sont accessibles :
```bash
# L'IP de l'instance est disponible dans les outputs Terraform
curl http://<EC2_IP>:8000/health  # API
curl http://<EC2_IP>:5000         # MLflow
curl http://<EC2_IP>:9090         # Prometheus
```

### 7. En cas d'Erreur
- Vérifiez les logs GitHub Actions
- Connectez-vous à l'instance EC2 pour vérifier les logs Docker :
  ```bash
  ssh -i ~/.ssh/mlops-key.pem ubuntu@<EC2_IP>
  docker-compose logs
  ```