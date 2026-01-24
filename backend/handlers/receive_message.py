import json
import os
import sys
import uuid
from datetime import datetime
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.dynamodb_client import DynamoDBClient
from shared.sqs_client import SQSClient
from shared.websocket_client import WebSocketClient

dynamodb = DynamoDBClient()
sqs = SQSClient()
websocket = WebSocketClient()

def lambda_handler(event, context):
    """
    Maneja el envío de mensajes.
    
    Flujo:
    1. Recibe mensaje del cliente por WebSocket
    2. Guarda en DynamoDB
    3. Encola en SQS para análisis
    4. Envía al destinatario por WebSocket
    """
    
    try:
        connection_id = event['requestContext']['connectionId']
        
        # Robust fetch of sender_id (handles local offline mode quirks)
        sender_id = event['requestContext'].get('authorizer', {}).get('claims', {}).get('sub')
        if not sender_id:
            sender_id = event['requestContext'].get('authorizer', {}).get('principalId')
        
        body = json.loads(event.get('body', '{}'))
        
        # Fallback for dev: trust body if auth context is missing
        if not sender_id:
             sender_id = body.get('data', {}).get('senderId') or 'user_dev'

        action = body.get('action')
        
        if action != 'sendMessage':
            return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid action'})}
        
        data = body.get('data', {})
        receiver_id = data.get('receiverId')
        content = data.get('content')
        conversation_id = data.get('conversationId')
        
        if not all([receiver_id, content, conversation_id]):
            return {'statusCode': 400, 'body': json.dumps({'error': 'Missing required fields'})}
        
        # Validar existencia del usuario receptor
        receiver_user = dynamodb.get_user(receiver_id)
        if not receiver_user:
            return {'statusCode': 400, 'body': json.dumps({'error': f"User '{receiver_id}' does not exist"})}

        message_id = f"msg_{uuid.uuid4().hex[:12]}"
        timestamp = int(datetime.utcnow().timestamp() * 1000)
        
        message_data = {
            'messageId': message_id,
            'senderId': sender_id,
            'receiverId': receiver_id,
            'content': content
        }
        
        if not dynamodb.save_message(conversation_id, timestamp, message_data):
            return {'statusCode': 500, 'body': json.dumps({'error': 'Failed to save message'})}

        # Actualizar metadatos de la conversación
        conversation_data = {
            'participant1': sender_id,
            'participant2': receiver_id,
            'lastMessage': content,
            'lastMessageTime': timestamp
        }
        dynamodb.update_conversation(conversation_id, conversation_data)
        
        sqs_message = {
            'messageId': message_id,
            'conversationId': conversation_id,
            'senderId': sender_id,
            'receiverId': receiver_id,
            'content': content,
            'timestamp': timestamp
        }
        
        sqs.send_message(sqs_message)
        
        if receiver_user and receiver_user.get('isOnline'):
            receiver_connection_id = receiver_user.get('connectionId')
            
            websocket_message = {
                'action': 'messageReceived',
                'data': {
                    'messageId': message_id,
                    'senderId': sender_id,
                    'content': content,
                    'timestamp': timestamp,
                    'status': 'delivered'
                }
            }
            
            websocket.send_message(receiver_connection_id, websocket_message)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'messageId': message_id,
                'timestamp': timestamp
            })
        }
        
    except Exception as e:
        print(f"Error in ReceiveMessage: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
