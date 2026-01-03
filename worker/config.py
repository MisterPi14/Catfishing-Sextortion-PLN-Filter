import os
from dotenv import load_dotenv

load_dotenv()

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_ENDPOINT_URL = os.getenv('AWS_ENDPOINT_URL') # Para LocalStack

# SQS Configuration
SQS_QUEUE_URL = os.getenv('SQS_QUEUE_URL')

# DynamoDB Configuration
DYNAMODB_TABLE = os.getenv('DYNAMODB_TABLE', 'pln-filter-backend-local-messages')

# Lambda Configuration
NOTIFY_USER_LAMBDA_NAME = os.getenv('NOTIFY_USER_LAMBDA_NAME', 'notify_user')

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral')

# Risk Detection Configuration
RISK_THRESHOLD = float(os.getenv('RISK_THRESHOLD', '0.7'))
THREAT_TYPES = ['sextorsion', 'catfishing', 'scam', 'harassment']

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
