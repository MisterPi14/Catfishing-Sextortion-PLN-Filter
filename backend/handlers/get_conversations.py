import json
import os
import sys
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.dynamodb_client import DynamoDBClient
from shared.websocket_client import WebSocketClient

dynamodb = DynamoDBClient()
websocket = WebSocketClient()


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def lambda_handler(event, context):
    try:
        user_id = None
        request_context = event.get('requestContext', {})
        authorizer = request_context.get('authorizer', {})

        claims = authorizer.get('claims', {})
        if claims:
            user_id = claims.get('sub')

        if not user_id:
            user_id = authorizer.get('principalId') or authorizer.get('sub')

        if not user_id:
            connection_id = request_context.get('connectionId')
            if connection_id:
                user = dynamodb.get_user_by_connection_id(connection_id)
                if user:
                    user_id = user.get('userId')

        if not user_id:
            return {'statusCode': 401, 'body': json.dumps({'error': 'Unauthorized - User not found'})}

        connection_id = request_context.get('connectionId')
        if not connection_id:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Missing connectionId'})}

        body = json.loads(event.get('body', '{}'))
        action = body.get('action')

        if action != 'getConversations':
            return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid action'})}

        conversations = dynamodb.get_user_conversations(user_id)

        websocket.send_message(connection_id, {
            'action': 'conversationsList',
            'data': {
                'conversations': conversations,
                'total': len(conversations)
            }
        })

        return {'statusCode': 200, 'body': json.dumps({'success': True})}
    except Exception as e:
        print(f"Error in getConversations: {str(e)}")
        if request_context.get('connectionId'):
            websocket.send_message(request_context['connectionId'], {
                'action': 'error',
                'data': {'error': str(e)}
            })

        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
