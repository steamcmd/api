import utils.config
import logging
import pika
import json


def connect():
    """
    Parse RabbitMQ config and connect.
    """

    try:
        credentials = pika.PlainCredentials(
            utils.config.rabbitmq_user, utils.config.rabbitmq_password
        )
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=utils.config.rabbitmq_host,
                port=int(utils.config.rabbitmq_port),
                credentials=credentials,
            )
        )
    except Exception as error:
        logging.error(f"Failed to connect to RabbitMQ with error: {error}")
        return False

    return connection


def publish(queue: str, message: str):
    """
    Publish a message to the specified RabbitMQ queue.
    """

    connection = connect()
    if not connection:
        return False
    try:
        channel = connection.channel()
        channel.queue_declare(queue=queue, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=queue,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2),  # make message persistent
        )
        connection.close()
        return True
    except Exception as error:
        logging.error(f"Failed to publish message to RabbitMQ: {error}")
        return False


def read(queue: str):
    """
    Read (consume) one message from the specified RabbitMQ queue.
    """

    connection = connect()
    if not connection:
        return False
    try:
        channel = connection.channel()
        method_frame, header_frame, body = channel.basic_get(queue=queue, auto_ack=True)
        connection.close()
        if method_frame:
            return body.decode("utf-8") if isinstance(body, bytes) else body
        else:
            return None
    except Exception as error:
        logging.error(f"Failed to read message from RabbitMQ: {error}")
        return False


def consume(callback, queue: str = "tasks", auto_ack: bool = True):
    """
    Continuously listen to the specified RabbitMQ queue and call the callback for each message.
    The callback should accept three arguments: channel, method, body.
    """

    connection = connect()
    if not connection:
        logging.error(
            "Failed to connect to RabbitMQ for consuming queue", extra={"queue": queue}
        )
        return None
    try:
        channel = connection.channel()
        channel.queue_declare(queue=queue, durable=True)

        def _callback(channel, method, properties, body):
            try:
                callback(channel, method, body)
            except Exception as err:
                logging.error(
                    "Error in message callback", extra={"rabbitmq_error": err}
                )

        channel.basic_consume(
            queue=queue, on_message_callback=_callback, auto_ack=auto_ack
        )
        logging.info("Consuming queue", extra={"queue": queue})
        channel.start_consuming()

    except Exception as err:
        logging.error(
            "Failed to consume messages from RabbitMQ", extra={"rabbitmq_error": err}
        )
        return None

    return True


def message(type: str, data: dict = {}, queue: str = "tasks"):
    """
    Construct JSON message with set format based on
    function input for the RabbitMQ message queue.
    Type must be one of existing tasks.
    """

    # Check if correct status input value is used
    if type not in utils.config.tasks_list:
        logging.error("Invalid task type provided", extra={"task": type})

    # Construct JSON message
    message = {"type": type, "data": data}
    # Publish message to RabbitMQ queue
    status = publish(queue, json.dumps(message))
    if not status:
        return None

    return status
