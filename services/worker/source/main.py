"""
Worker Service.
"""

# Patch blocking modules for gevent
from gevent import monkey

_ = monkey.patch_all()

# Import modules
import utils.rabbitmq
import utils.steam
import utils.helper
import logging
import signal
import json
import sys
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic


## Initialize
def main():
    # Set up signal handlers for graceful shutdown
    def signal_handler(signum: int, _) -> None:
        logging.info("Received shutdown signal %s...", signum)
        sys.exit(0)

    _ = signal.signal(signal.SIGTERM, signal_handler)
    _ = signal.signal(signal.SIGINT, signal_handler)

    # Initialize steam client
    client = utils.steam.init_client()
    if client is None:
        logging.warning("Steam client not available yet. Retrying on first message")

    # Import tasks dynamically
    import tasks

    utils.helper.import_tasks()

    # Process message based on type definition
    def process_message(_channel: BlockingChannel, _method: Basic.Deliver, body: bytes):
        nonlocal client

        # Set message JSON object for queue
        try:
            # Reconnect steam client if not logged on
            client = utils.steam.ensure_client(client)
            if client is None:
                raise RuntimeError("Steam client is not available")

            message = body.decode("utf-8")
            message = json.loads(message)
            function = message["type"]
            logging.info("Received message from queue", extra={"payload": message})

            # Execute the function based on the function variable
            task_module = getattr(tasks, function)
            if message["data"]:
                task_module.main(client, message["data"])
            else:
                task_module.main(client)

        except Exception as err:
            logging.error(
                "Failed processing message from queue",
                extra={"error": repr(err), "payload_raw": body},
            )

    # Wait for messages on RabbitMQ queue
    try:
        utils.rabbitmq.consume(process_message)

    # Shutdown worker if shutdown signal is received
    except (KeyboardInterrupt, SystemExit):
        logging.info("Received shutdown signal...")

    logging.info("Logging out steam client..")
    utils.steam.close_client(client)


if __name__ == "__main__":
    main()
