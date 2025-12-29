def lambda_handler(event, context):
    """
    Simple Lambda Authorizer that allows all requests.
    In a real app, you would validate the token here.
    """
    return {
        "principalId": "user",
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": event["methodArn"]
                }
            ]
        }
    }
