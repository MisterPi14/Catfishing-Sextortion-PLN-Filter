import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from shared.dynamodb_client import DynamoDBClient

dynamodb = DynamoDBClient()

def lambda_handler(event, context):
    """
    Maneja la conexión WebSocket ($connect).
    Guarda la asociación connectionId <-> userId.
    """
    print("DEBUG: CONNECT HANDLER EXECUTED")
    
    try:
        connection_id = event['requestContext']['connectionId']
        
        # Obtener userId del autorizador (ahora corregido en auth.py)
        user_id = event['requestContext'].get('authorizer', {}).get('principalId')
        
        if not user_id:
             print("ERROR: No principalId found in requestContext")
             return {'statusCode': 401, 'body': 'Unauthorized'}

        print(f"New connection: {connection_id} for user: {user_id}")
        
        # Registrar conexión en DynamoDB
        if dynamodb.update_user_connection(user_id, connection_id):
            return {'statusCode': 200, 'body': 'Connected'}
        else:
            return {'statusCode': 500, 'body': 'Failed to update user connection'}

    except Exception as e:
        print(f"Error in connect: {e}")
        return {'statusCode': 500, 'body': 'Internal Server Error'}

def disconnect_handler(event, context):
    print("DEBUG: DISCONNECT HANDLER EXECUTED")
    # Opcional: Marcar usuario como desconectado
    return {'statusCode': 200, 'body': 'Disconnected'}
