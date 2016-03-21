from .worker import Consumer
from .arguments import Arguments


def start_worker(broker_ip, broker_port, username, password, incoming_queue, result_exchange, result_routing, result_queue, topic_type):
    arguments = Arguments()
    arguments.broker_ip = broker_ip
    arguments.broker_port = broker_port
    arguments.username = username
    arguments.password = password
    arguments.incoming_queue = incoming_queue
    arguments.result_exchange = result_exchange
    arguments.result_routing = result_routing
    arguments.result_queue = result_queue
    arguments.topic_type = topic_type
    consumer = Consumer(arguments)
    consumer.consume()
