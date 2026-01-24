def lambda_handler(event, context):
    """
    Simple Lambda Authorizer.
    Recupera el token (username) de los query params y lo usa como principalId.
    """
    print(f"DEBUG AUTH EVENT: {event}") # Debug print
    
    # Intentar obtener el token de query params (WebSocket) o headers (HTTP)
    token = None
    if event.get('queryStringParameters'):
        token = event.get('queryStringParameters').get('token')
    
    if not token and event.get('headers'):
        # Case insensitive header lookup
        headers = {k.lower(): v for k, v in event.get('headers').items()}
        token = headers.get('authorization')
        
    # Si no hay token, rechazamos o usamos un default (para pruebas)
    principal_id = token if token else "user"

    method_arn = event.get('methodArn')
    if not method_arn:
        # Fallback for some local environments
        method_arn = event.get('routeArn', '*')

    return {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": "*" # Allow all for local testing to avoid ARN mismatch issues
                }
            ]
        }
    }
