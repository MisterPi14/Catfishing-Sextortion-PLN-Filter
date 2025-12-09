import boto3
import json
import os

class WebSocketClient:
    def __init__(self):
        self.api_gateway = boto3.client('apigatewaymanagementapi', 
                                       endpoint_url=os.getenv('WEBSOCKET_API_ENDPOINT'),
                                       region_name=os.getenv('AWS_REGION', 'us-east-1'))

    def send_message(self, connection_id, message_data):
        """Envía un mensaje a un cliente conectado por WebSocket"""
        try:
            self.api_gateway.post_to_connection(
                ConnectionId=connection_id,
                Data=json.dumps(message_data)
            )
            return True
        except Exception as e:
            print(f"Error sending WebSocket message: {str(e)}")
            return False

    def broadcast_message(self, connection_ids, message_data):
        """Envía un mensaje a múltiples clientes"""
        results = []
        for conn_id in connection_ids:
            result = self.send_message(conn_id, message_data)
            results.append(result)
        return all(results)
