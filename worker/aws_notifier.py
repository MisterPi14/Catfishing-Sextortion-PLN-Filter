import boto3
import json
import logging
from decimal import Decimal
from config import AWS_REGION, NOTIFY_USER_LAMBDA_NAME, AWS_ENDPOINT_URL, DYNAMODB_TABLE

logger = logging.getLogger(__name__)

class AWSNotifier:
    def __init__(self):
        self.lambda_client = boto3.client(
            'lambda', 
            region_name=AWS_REGION,
            endpoint_url=AWS_ENDPOINT_URL
        )
        self.dynamodb = boto3.resource(
            'dynamodb', 
            region_name=AWS_REGION,
            endpoint_url=AWS_ENDPOINT_URL
        )

    def notify_user(self, user_id, message_id, threat_type, confidence, risk_level):
        """Invoca la Lambda NotifyUser para alertar al usuario"""
        try:
            payload = {
                'userId': user_id,
                'messageId': message_id,
                'threatType': threat_type,
                'confidence': confidence,
                'riskLevel': risk_level
            }
            
            response = self.lambda_client.invoke(
                FunctionName=NOTIFY_USER_LAMBDA_NAME,
                InvocationType='Event',  # Asincrónico
                Payload=json.dumps(payload)
            )
            
            logger.info(f"Notification sent to user {user_id} for message {message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error notifying user: {str(e)}")
            return False

    def update_message_analysis(self, conversation_id, timestamp, analysis_data):
        """Actualiza el análisis de un mensaje en DynamoDB"""
        try:
            table = self.dynamodb.Table(DYNAMODB_TABLE)

            # Preparar datos y convertir floats a Decimal
            analysis_payload = {
                'analyzed': True,
                'riskLevel': analysis_data.get('risk_level'),
                'threatType': analysis_data.get('threat_type'),
                'confidence': analysis_data.get('confidence')
            }

            analysis_to_save = json.loads(
                json.dumps(analysis_payload), 
                parse_float=Decimal
            )
            
            table.update_item(
                Key={
                    'conversationId': conversation_id,
                    'timestamp': int(timestamp)
                },
                UpdateExpression='SET riskAnalysis = :analysis',
                ExpressionAttributeValues={
                    ':analysis': analysis_to_save
                }
            )
            
            logger.info(f"Message analysis updated for {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating message analysis: {str(e)}")
            raise e
