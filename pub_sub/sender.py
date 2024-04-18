import pika
from time import sleep
from random import randint, choice
from os import environ

ROUTING_CHOICES_PRIMARY = ['backend','frontend']
ROUTING_CHOICES_SECONDARY = ['pay', 'validation', 'verification', 'info']

class RMQSender:
    def __init__(self):
        host = environ.get("HOST", "localhost")
        print("HOST", host)
        url = f"amqp://rmuser:rmpassword@{host}:5672"
        params = pika.URLParameters(url)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
    
    def create_exchange(self, name : str, type : str):
        self.channel.exchange_declare(exchange=name, exchange_type=type)

    def create_queue(self, queue_name : str, exchamge_name : str, queue_bind : str):
        self.channel.queue_declare(queue=queue_name)
        self.channel.queue_bind(exchange=exchamge_name, queue=queue_name, routing_key=queue_bind)

    def send_msg(self, msg, exchange_name: str, routing_key: str):
        self.channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=msg)

    def close(self):
        self.connection.close()

def event_creator():
    msg = str(randint(0,1000))
    routing_key = f"{choice(ROUTING_CHOICES_PRIMARY)}.{choice(ROUTING_CHOICES_SECONDARY)}"
    return msg, routing_key

def main():
    sender = RMQSender()
    sender.create_exchange('mainex', 'topic')
    while True:
        try:
            msg, routing_key = event_creator()
            sender.send_msg(msg, "mainex", routing_key)
            print(f"Sender sent msg {msg} with routing key {routing_key}")
            sleep(3)
        except KeyboardInterrupt:
            print("Kbint closing...")
            sender.close()
            exit()

if __name__ == "__main__":
    main()