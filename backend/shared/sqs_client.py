import boto3
import json
import os

class SQSClient:
    def __init__(self):
        is_offline = os.getenv('IS_OFFLINE')
        
        if is_offline:
            self.sqs = boto3.client(
                'sqs',
                region_name='localhost',
                endpoint_url='http://localhost:9324', # Puerto estándar de ElasticMQ/SQS local
                aws_access_key_id='DEFAULT_ACCESS_KEY',
                aws_secret_access_key='DEFAULT_SECRET_KEY'
            )
        else:
            self.sqs = boto3.client('sqs', region_name=os.getenv('AWS_REGION', 'us-east-1'))
            
        self.queue_url = os.getenv('SQS_QUEUE_URL')

    def send_message(self, message_data):
        """Envía un mensaje a la cola SQS para análisis"""
        try:
            response = self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message_data)
            )
            return response.get('MessageId')
        except Exception as e:
            print(f"Error sending message to SQS: {str(e)}")
            return None

    def receive_messages(self, max_messages=1, wait_time=20):
        """Recibe mensajes de la cola SQS"""
        try:
            response = self.sqs.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=wait_time
            )
            return response.get('Messages', [])
        except Exception as e:
            print(f"Error receiving messages from SQS: {str(e)}")
            return []

    def delete_message(self, receipt_handle):
        """Elimina un mensaje de la cola después de procesarlo"""
        try:
            self.sqs.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )
            return True
        except Exception as e:
            print(f"Error deleting message from SQS: {str(e)}")
            return False
