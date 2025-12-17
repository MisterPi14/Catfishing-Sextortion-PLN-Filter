import boto3
import os
from decimal import Decimal
from datetime import datetime

class DynamoDBClient:
    def __init__(self):
        is_offline = os.getenv('IS_OFFLINE')
        print(f"DEBUG: IS_OFFLINE={is_offline}") # Debug print
        
        if is_offline:
            print("DEBUG: Connecting to Local DynamoDB")
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name='us-east-1',
                endpoint_url='http://localhost:8000',
                aws_access_key_id='fake',
                aws_secret_access_key='fake'
            )
        else:
            self.dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'us-east-1'))
            
        self.messages_table = self.dynamodb.Table(os.getenv('DYNAMODB_TABLE', 'ChatMessages'))
        self.users_table = self.dynamodb.Table(os.getenv('DYNAMODB_USERS_TABLE', 'Users'))
        self.conversations_table = self.dynamodb.Table(os.getenv('DYNAMODB_CONVERSATIONS_TABLE', 'Conversations'))

    def save_message(self, conversation_id, timestamp, message_data):
        """Guarda un mensaje en DynamoDB"""
        try:
            self.messages_table.put_item(Item={
                'conversationId': conversation_id,
                'timestamp': Decimal(str(timestamp)),
                'messageId': message_data['messageId'],
                'senderId': message_data['senderId'],
                'receiverId': message_data['receiverId'],
                'content': message_data['content'],
                'status': message_data.get('status', 'pending'),
                'riskAnalysis': {
                    'analyzed': False,
                    'riskLevel': None,
                    'threatType': None,
                    'confidence': None
                },
                'createdAt': datetime.utcnow().isoformat() + 'Z'
            })
            return True
        except Exception as e:
            print(f"Error saving message: {str(e)}")
            return False

    def get_messages(self, conversation_id, limit=50, offset=0):
        """Obtiene mensajes de una conversación"""
        try:
            response = self.messages_table.query(
                KeyConditionExpression='conversationId = :conv_id',
                ExpressionAttributeValues={':conv_id': conversation_id},
                Limit=limit,
                ScanIndexForward=False  # Orden descendente (más recientes primero)
            )
            return response.get('Items', [])
        except Exception as e:
            print(f"Error getting messages: {str(e)}")
            return []

    def update_message_analysis(self, conversation_id, timestamp, analysis_data):
        """Actualiza el análisis de riesgo de un mensaje"""
        try:
            self.messages_table.update_item(
                Key={
                    'conversationId': conversation_id,
                    'timestamp': Decimal(str(timestamp))
                },
                UpdateExpression='SET riskAnalysis = :analysis',
                ExpressionAttributeValues={
                    ':analysis': {
                        'analyzed': True,
                        'riskLevel': analysis_data.get('riskLevel'),
                        'threatType': analysis_data.get('threatType'),
                        'confidence': Decimal(str(analysis_data.get('confidence', 0)))
                    }
                }
            )
            return True
        except Exception as e:
            print(f"Error updating message analysis: {str(e)}")
            return False

    def save_user(self, user_id, user_data):
        """Guarda o actualiza información de usuario"""
        try:
            self.users_table.put_item(Item={
                'userId': user_id,
                'email': user_data.get('email'),
                'username': user_data.get('username'),
                'connectionId': user_data.get('connectionId'),
                'isOnline': user_data.get('isOnline', True),
                'lastSeen': Decimal(str(user_data.get('lastSeen', int(datetime.utcnow().timestamp() * 1000)))),
                'createdAt': user_data.get('createdAt', datetime.utcnow().isoformat() + 'Z')
            })
            return True
        except Exception as e:
            print(f"Error saving user: {str(e)}")
            return False

    def get_user(self, user_id):
        """Obtiene información de un usuario"""
        try:
            response = self.users_table.get_item(Key={'userId': user_id})
            return response.get('Item')
        except Exception as e:
            print(f"Error getting user: {str(e)}")
            return None

    def update_user_connection(self, user_id, connection_id):
        """Actualiza el connectionId de un usuario"""
        try:
            self.users_table.update_item(
                Key={'userId': user_id},
                UpdateExpression='SET connectionId = :conn_id, isOnline = :online, lastSeen = :last_seen',
                ExpressionAttributeValues={
                    ':conn_id': connection_id,
                    ':online': True,
                    ':last_seen': Decimal(str(int(datetime.utcnow().timestamp() * 1000)))
                }
            )
            return True
        except Exception as e:
            print(f"Error updating user connection: {str(e)}")
            return False
