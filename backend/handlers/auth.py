def lambda_handler(event, context):
    """
    Simple Lambda Authorizer.
    """
    print(f"DEBUG AUTH EVENT: {event}") # Debug print
    
    method_arn = event.get('methodArn')
    if not method_arn:
        # Fallback for some local environments
        method_arn = event.get('routeArn', '*')

    return {
        "principalId": "user",
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
