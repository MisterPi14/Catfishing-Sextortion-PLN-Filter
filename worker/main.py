import logging
import time
from config import LOG_LEVEL
from sqs_listener import SQSListener
from llm_processor import LLMProcessor
from aws_notifier import AWSNotifier

# Configurar logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PLNFilterWorker:
    def __init__(self):
        self.sqs_listener = SQSListener()
        self.llm_processor = LLMProcessor()
        self.aws_notifier = AWSNotifier()
        self.running = True

    def process_message(self, message_data):
        """Procesa un mensaje: analiza y notifica si hay riesgo"""
        try:
            message_id = message_data.get('messageId')
            conversation_id = message_data.get('conversationId')
            receiver_id = message_data.get('receiverId')
            content = message_data.get('content')
            timestamp = message_data.get('timestamp')
            
            logger.info(f"Processing message {message_id}")
            
            # 1. Analizar con Ollama
            analysis = self.llm_processor.analyze_message(content)
            
            logger.info(f"Analysis result: {analysis}")
            
            # 2. Actualizar análisis en DynamoDB
            self.aws_notifier.update_message_analysis(
                conversation_id,
                timestamp,
                analysis
            )
            
            # 3. Si hay amenaza, notificar al usuario
            if analysis['threat_detected']:
                logger.warning(f"Threat detected in message {message_id}: {analysis['threat_type']}")
                
                self.aws_notifier.notify_user(
                    user_id=receiver_id,
                    message_id=message_id,
                    threat_type=analysis['threat_type'],
                    confidence=analysis['confidence'],
                    risk_level=analysis['risk_level']
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return False

    def run(self):
        """Loop principal del worker"""
        logger.info("PLN Filter Worker started")
        
        while self.running:
            try:
                # Recibir mensajes de SQS
                messages = self.sqs_listener.receive_messages(max_messages=1, wait_time=20)
                
                if not messages:
                    logger.debug("No messages received from SQS")
                    continue
                
                for message in messages:
                    # Parsear mensaje
                    parsed = self.sqs_listener.parse_message(message)
                    
                    if not parsed:
                        continue
                    
                    # Procesar
                    if self.process_message(parsed['data']):
                        # Eliminar de la cola si se procesó correctamente
                        self.sqs_listener.delete_message(parsed['receipt_handle'])
                    else:
                        logger.warning(f"Failed to process message, will retry")
                        # El mensaje volverá a la cola después del timeout
                
            except KeyboardInterrupt:
                logger.info("Worker interrupted by user")
                self.running = False
            except Exception as e:
                logger.error(f"Unexpected error in worker loop: {str(e)}")
                time.sleep(5)  # Esperar antes de reintentar

if __name__ == '__main__':
    worker = PLNFilterWorker()
    worker.run()
