import json

def lambda_handler(event, context):
    """
    Versión Minimalista de connect.py para debuggear error 500.
    """
    print("DEBUG: CONNECT HANDLER EXECUTED")
    
    # Intentamos leer el connectionId solo para loggearlo
    try:
        conn_id = event.get('requestContext', {}).get('connectionId', 'unknown')
        print(f"New connection: {conn_id}")
    except:
        pass

    return {'statusCode': 200, 'body': 'Connected'}

def disconnect_handler(event, context):
    print("DEBUG: DISCONNECT HANDLER EXECUTED")
    return {'statusCode': 200, 'body': 'Disconnected'}
