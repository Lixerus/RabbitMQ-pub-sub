import pika
from time import sleep
from typing import Callable
import logging
import sys
from os import environ

DEAD_EXCHANGE_NAME = "deadex"
DEAD_QUEUE_NAME = "deadque"
DEAD_ROUTING_KEY = "deadroutingkey"

class RMQReciever:
    def __init__(self):
        host = environ.get("HOST", "localhost")
        print(host)
        url = f"amqp://rmuser:rmpassword@{host}:5672"
        params = pika.URLParameters(url)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        self.dead_queue_ready = False
    
    def create_exchange(self, name : str, type : str):
        self.channel.exchange_declare(exchange=name, exchange_type=type)

    def prepare_dead_queue(self):
        self.channel.exchange_declare(DEAD_EXCHANGE_NAME, 'fanout')
        self.channel.queue_declare(DEAD_QUEUE_NAME)
        self.channel.queue_bind(DEAD_QUEUE_NAME, DEAD_EXCHANGE_NAME, DEAD_ROUTING_KEY)
        self.dead_queue_ready = True

    def create_queue(self, queue_name : str, exchamge_name : str, queue_bind : str):
        if not self.dead_queue_ready:
            self.prepare_dead_queue()
        arguments = {
                "x-dead-letter-exchange": DEAD_EXCHANGE_NAME,
                "x-dead-letter-routing-key": DEAD_ROUTING_KEY,
        }
        self.channel.queue_declare(queue=queue_name, arguments=arguments)
        self.channel.queue_bind(exchange=exchamge_name, queue=queue_name, routing_key=queue_bind)

    def subscribe_callback(self, queue_name:str, callback : Callable):
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback)

    def start_consuming(self):
        self.channel.start_consuming()

    def close(self):
        self.connection.close()

def main():

    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='event.log', filemode='w' ,format='%(levelname)s:%(message)s', encoding='utf-8', level=logging.INFO)
    logger.addHandler(logging.StreamHandler(sys.stdout))

    def consumer(channel, method_frame, header_frame, body):
        msg = body.decode("utf-8")
        sleep(1)
        try:
            if method_frame.delivery_tag % 5 == 0:
                raise ValueError
            else:
                logger.info(f"Recieved msg {msg} acked")
                channel.basic_ack(delivery_tag=method_frame.delivery_tag, multiple=False)
        except:
            logger.warning(f"Recieved msg {msg} nacked and sent to DLX")
            channel.basic_nack(delivery_tag=method_frame.delivery_tag, multiple=False, requeue=False)
        return
    

    reciever = RMQReciever()
    reciever.create_exchange('mainex', 'topic')
    reciever.create_queue('backend_event', 'mainex', 'backend.#')
    reciever.create_queue('frontend_event', 'mainex', 'frontend.#')
    reciever.subscribe_callback('backend_event', consumer)
    reciever.subscribe_callback('frontend_event', consumer)
    while True:
        try:
            reciever.start_consuming()
            print("Started consuming")
        except KeyboardInterrupt:
            print("Kbint closing...")
            reciever.close()
            exit()

if __name__ == "__main__":
    main()