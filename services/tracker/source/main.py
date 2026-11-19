"""
Tracker Service.
"""

# Patch blocking modules for gevent
from gevent import monkey

_ = monkey.patch_all()

# Import modules
import utils.redis
import utils.rabbitmq
import utils.steam
import logging
import gevent
import signal
import sys

# Set loop settings
POLL_INTERVAL = 0.3
MAX_BACKOFF = 60
MAX_CONSECUTIVE_FAILURES = 20


## Initialize
def main():
    # Set up signal handlers for graceful shutdown
    def signal_handler(signum: int, _) -> None:
        logging.info("Received shutdown signal..", extra={"signum": signum})
        sys.exit(0)

    _ = signal.signal(signal.SIGTERM, signal_handler)
    _ = signal.signal(signal.SIGINT, signal_handler)

    previous_change_number = 0
    client = None
    failures = 0

    try:
        while True:
            try:
                # Reconnect steam client if not logged on
                client = utils.steam.ensure_client(client)
                if client is None:
                    raise RuntimeError("Steam client is not available")

                # Read latest change number from cache if not set in memory
                if previous_change_number == 0:
                    cached_change_number = utils.redis.read("_state.change_number")
                    if cached_change_number:
                        previous_change_number = int(cached_change_number)

                # Retrieve latest change number directly from Steam
                change_number = utils.steam.get_change_number(client)
                if change_number is None:
                    raise RuntimeError("Retrieving change number failed")

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
                    if app_list is None:
                        raise RuntimeError("Retrieving changed apps failed")

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
                        if not utils.rabbitmq.message("info", {"id": appid}):
                            raise RuntimeError(
                                "Publishing app info message failed for app "
                                + str(appid)
                            )

                    # Make previous change number the current
                    utils.redis.write("_state.change_number", change_number)
                    previous_change_number = change_number

                failures = 0

                # Wait shortly before continueing in the loop
                gevent.sleep(POLL_INTERVAL)

            except Exception as err:
                # Reset steam client and wait before retrying
                failures += 1
                logging.error(
                    "Failure during loop",
                    extra={"error": repr(err), "consecutive_failures": failures},
                )
                utils.steam.close_client(client)
                client = None

                if failures >= MAX_CONSECUTIVE_FAILURES:
                    logging.critical(
                        "Too many consecutive failures. Exiting so the service is restarted",
                        extra={"consecutive_failures": failures},
                    )
                    sys.exit(1)

                gevent.sleep(min(2**failures, MAX_BACKOFF))

    # Shutdown tracker if shutdown signal is received
    except (KeyboardInterrupt, SystemExit):
        logging.info("Shutting down tracker..")
        logging.info("Logging out steam client..")
        utils.steam.close_client(client)
        raise


if __name__ == "__main__":
    main()
