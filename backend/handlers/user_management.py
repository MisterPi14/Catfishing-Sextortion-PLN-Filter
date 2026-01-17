import json
import os
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

# Inicializar DynamoDB
# En local o nube, serverless inyecta las variables de entorno o usamos boto3 por defecto
# Inicializar DynamoDB usando configuración centralizada
is_offline = os.environ.get('IS_OFFLINE') == 'true'
region = os.environ.get('AWS_REGION', 'us-east-1')

if is_offline:
    endpoint_url = os.environ.get('DYNAMODB_ENDPOINT', 'http://localhost:4566')
    dynamodb = boto3.resource(
        'dynamodb',
        region_name=region,
        endpoint_url=endpoint_url,
        aws_access_key_id='local',
        aws_secret_access_key='local'
    )
else:
    dynamodb = boto3.resource('dynamodb', region_name=region)

USERS_TABLE = os.environ['DYNAMODB_USERS_TABLE']

def register(event, context):
    try:
        data = json.loads(event.get('body', '{}'))
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Username and password are required'})
            }

        table = dynamodb.Table(USERS_TABLE)

        # Verificar si el usuario ya existe
        response = table.get_item(Key={'userId': username})
        if 'Item' in response:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'User already exists'})
            }

        # Guardar usuario (En prod deberíamos hashear la password)
        # Para este MVP guardamos simple.
        user_item = {
            'userId': username, # Usamos username como ID
            'password': password,
            'createdAt': datetime.utcnow().isoformat()
        }

        table.put_item(Item=user_item)

        return {
            'statusCode': 201,
            'body': json.dumps({'message': 'User registered successfully', 'userId': username})
        }

    except Exception as e:
        print(f"Error in register: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }

def login(event, context):
    try:
        data = json.loads(event.get('body', '{}'))
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Username and password are required'})
            }

        table = dynamodb.Table(USERS_TABLE)
        response = table.get_item(Key={'userId': username})

        if 'Item' not in response:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Invalid credentials'})
            }

        user = response['Item']
        
        # Verificación simple de contraseña
        if user.get('password') != password:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Invalid credentials'})
            }

        # Generar un token simple (en prod usar JWT)
        # Retornamos el mismo userId como token para simplificar ya que el Auth lambda es dummy
        token = username 
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'token': token,
                'user': {
                    'userId': username,
                    'username': username
                }
            })
        }

    except Exception as e:
        print(f"Error in login: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
