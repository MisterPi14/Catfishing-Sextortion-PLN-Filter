import boto3
import json
import logging
from config import AWS_REGION, SQS_QUEUE_URL

logger = logging.getLogger(__name__)

class SQSListener:
    def __init__(self):
        self.sqs = boto3.client('sqs', region_name=AWS_REGION)
        self.queue_url = SQS_QUEUE_URL

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
            logger.error(f"Error receiving messages from SQS: {str(e)}")
            return []

    def delete_message(self, receipt_handle):
        """Elimina un mensaje de la cola después de procesarlo"""
        try:
            self.sqs.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )
            logger.info(f"Message deleted from SQS")
            return True
        except Exception as e:
            logger.error(f"Error deleting message from SQS: {str(e)}")
            return False

    def parse_message(self, message):
        """Parsea un mensaje de SQS"""
        try:
            body = json.loads(message['Body'])
            return {
                'receipt_handle': message['ReceiptHandle'],
                'data': body
            }
        except Exception as e:
            logger.error(f"Error parsing SQS message: {str(e)}")
            return None
