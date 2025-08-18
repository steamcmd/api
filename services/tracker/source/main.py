"""
Tracker Service.
"""

# Import modules
import utils.redis
import utils.rabbitmq
import utils.steam
import logging
import time
import signal
import sys


## Initialize
def main():
    # Set up signal handlers for graceful shutdown
    def signal_handler(signum: int, _) -> None:
        logging.info("Received shutdown signal..", extra={"signum": signum})
        sys.exit(0)

    _ = signal.signal(signal.SIGTERM, signal_handler)
    _ = signal.signal(signal.SIGINT, signal_handler)

    # Initialize steam client
    previous_change_number = 0
    client = utils.steam.init_client()

    try:
        while True:
            try:
                # Read latest change number from cache if not set in memory
                if previous_change_number == 0:
                    if utils.redis.read("_state.change_number"):
                        previous_change_number = int(
                            utils.redis.read("_state.change_number")
                        )

                # Retrieve latest change number directly from Steam
                change_number = utils.steam.get_change_number(client)

                if change_number == previous_change_number:
                    logging.info(
                        "Changenumber not changed",
                        extra={"change_number": change_number},
                    )
                else:
                    # Retrieve list of changed apps
                    app_list = utils.steam.get_changed_apps(
                        client, previous_change_number
                    )
                    logging.info(
                        "Changenumber changed",
                        extra={
                            "change_number": change_number,
                            "previous_change_number": previous_change_number,
                            "app_list": app_list,
                        },
                    )

                    # Store Changenumber to cache
                    flat_app_list = ",".join(str(appid) for appid in app_list)
                    utils.redis.write("change." + str(change_number), flat_app_list)

                    # Publish a message to RabbitMQ for each changed app
                    for appid in app_list:
                        # Set message JSON object and publish
                        utils.rabbitmq.message("info", {"id": appid})

                    # Make previous change number the current
                    utils.redis.write("_state.change_number", change_number)
                    previous_change_number = change_number

                # Wait shortly before continueing in the loop
                time.sleep(0.3)

            except Exception as err:
                logging.error("Failure during loop", extra={"error": err})
                break

        # Logout Steam Client if loop breaks
        client.logout()

    # Shutdown tracker if shutdown signal is received
    except (KeyboardInterrupt, SystemExit):
        logging.info("Received shutdown signal..")

    logging.info("Logging out steam client..")
    client.logout()


if __name__ == "__main__":
    main()
