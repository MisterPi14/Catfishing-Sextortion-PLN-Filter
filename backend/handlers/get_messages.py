import json
import os
import sys
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.dynamodb_client import DynamoDBClient

dynamodb = DynamoDBClient()

def decimal_default(obj):
    """Convertir Decimal a float para JSON"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    """
    Recupera el historial de mensajes de una conversación.
    
    Flujo:
    1. Recibe solicitud del cliente
    2. Consulta DynamoDB
    3. Retorna mensajes ordenados por timestamp
    """
    
    try:
        user_id = event['requestContext']['authorizer']['claims']['sub']
        
        body = json.loads(event.get('body', '{}'))
        action = body.get('action')
        
        if action != 'getMessages':
            return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid action'})}
        
        data = body.get('data', {})
        conversation_id = data.get('conversationId')
        limit = data.get('limit', 50)
        offset = data.get('offset', 0)
        
        if not conversation_id:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Missing conversationId'})}
        
        messages = dynamodb.get_messages(conversation_id, limit=limit)
        messages = messages[offset:offset + limit]
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'action': 'messagesHistory',
                'data': {
                    'conversationId': conversation_id,
                    'messages': messages,
                    'total': len(messages)
                }
            }, default=decimal_default)
        }
        
    except Exception as e:
        print(f"Error in GetMessages: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
