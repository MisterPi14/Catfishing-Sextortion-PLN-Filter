import json
import os
import sys
from decimal import Decimal

# Agregar la carpeta shared al path
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
        # Extraer información del evento
        # Intentar obtener usuario por connectionId primero (WebSocket)
        user_id = None
        connection_id = event.get('requestContext', {}).get('connectionId')
        
        if connection_id:
            user = dynamodb.get_user_by_connection_id(connection_id)
            if user:
                user_id = user['userId']
                
        # Fallback a authorizer claims (HTTP o si falla DB)
        if not user_id:
            try:
                claims = event['requestContext']['authorizer'].get('claims')
                if not claims: 
                    # Intenta extraer de authorizer plano (custom authorizer en local)
                    authorizer_data = event['requestContext']['authorizer']
                    user_id = authorizer_data.get('sub') or authorizer_data.get('principalId')
                else:
                    user_id = claims.get('sub')
            except (KeyError, TypeError):
                print(f"Error getting user_id. Context: {event.get('requestContext')}")
                pass
        
        if not user_id:
            return {'statusCode': 401, 'body': json.dumps({'error': 'Unauthorized - User not found'})}
        
        body = json.loads(event.get('body', '{}'))
        action = body.get('action')
        
        if action != 'getMessages':
            return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid action'})}
        
        data = body.get('data', {})
        conversation_id = data.get('conversationId')
        limit = data.get('limit', 50)
        offset = data.get('offset', 0)
        
        # Validar datos
        if not conversation_id:
             # Si no viene conversationId, intentar construirlo si tenemos participant
            data = body.get('data', {})
            participant = data.get('participant') # podria venir del front
            if not conversation_id and participant and user_id:
                 conversation_id = '_'.join(sorted([user_id, participant]))

        # Si aun falta
        if not conversation_id:
            # Fallback temporal para dev: intentar deducirlo del body si el front envio 'receiverId' en lugar de conversationId (error comun)
            receiver_id = data.get('receiverId')
            if receiver_id and user_id:
                conversation_id = '_'.join(sorted([user_id, receiver_id]))
            else:
                 return {'statusCode': 400, 'body': json.dumps({'error': 'Missing conversationId'})}
        
        # Obtener mensajes
        messages = dynamodb.get_messages(conversation_id, limit=limit)
        
        # Aplicar offset
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
