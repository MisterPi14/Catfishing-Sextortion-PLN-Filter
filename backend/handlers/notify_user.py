import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.dynamodb_client import DynamoDBClient
from shared.websocket_client import WebSocketClient

dynamodb = DynamoDBClient()
websocket = WebSocketClient()

def lambda_handler(event, context):
    """
    Envía alertas de riesgo al usuario.
    
    Flujo:
    1. Recibe solicitud del Worker local
    2. Obtiene connectionId del usuario
    3. Envía alerta por WebSocket
    """
    
    try:
        body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event
        
        user_id = body.get('userId')
        message_id = body.get('messageId')
        threat_type = body.get('threatType')
        confidence = body.get('confidence')
        risk_level = body.get('riskLevel')
        
        if not all([user_id, message_id, threat_type]):
            return {'statusCode': 400, 'body': json.dumps({'error': 'Missing required fields'})}
        
        user = dynamodb.get_user(user_id)
        if not user or not user.get('isOnline'):
            return {'statusCode': 404, 'body': json.dumps({'error': 'User not online'})}
        
        connection_id = user.get('connectionId')
        
        alert_message = {
            'action': 'riskAlert',
            'data': {
                'messageId': message_id,
                'threatType': threat_type,
                'confidence': confidence,
                'riskLevel': risk_level,
                'message': f'Alerta: Se detectó posible intento de {threat_type}'
            }
        }
        
        if websocket.send_message(connection_id, alert_message):
            return {
                'statusCode': 200,
                'body': json.dumps({'success': True, 'message': 'Alert sent'})
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Failed to send alert'})
            }
        
    except Exception as e:
        print(f"Error in NotifyUser: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
