"""
Tracker Service.
"""

# Import modules
import utils.config
import utils.redis
import utils.rabbitmq
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

    # Initialize tasks status
    tasks_lists = utils.config.tasks_list

    # Output startup message
    logging.info("Starting scheduler service..")
    for task in tasks_lists:
        logging.info(
            "Scheduled task active",
            extra={"task": task, "interval": tasks_lists[task]["interval"]},
        )

    try:
        while True:
            try:
                # Check if one of the tasks should be run
                for task in tasks_lists:
                    # Skip tasks with interval 0 or less
                    if tasks_lists[task]["interval"] <= 0:
                        continue

                    # Retrieve last timestamp the task ran
                    if "timestamp" not in tasks_lists[task]:
                        # Read last run time from cache
                        timestamp = utils.redis.read("_state.task." + task)
                        if not timestamp:
                            tasks_lists[task]["timestamp"] = 0
                        else:
                            tasks_lists[task]["timestamp"] = int(timestamp)

                    # Check if task needs to be run
                    current_timestamp = int(time.time())
                    if (
                        current_timestamp - tasks_lists[task]["timestamp"]
                        >= tasks_lists[task]["interval"]
                    ):

                        # Trigger overdue task with queue message
                        logging.info(
                            "Triggered overdue task",
                            extra={
                                "task": task,
                                "timestamp": tasks_lists[task]["timestamp"],
                            },
                        )
                        utils.rabbitmq.message(task)
                        tasks_lists[task]["timestamp"] = int(time.time())

                # Wait shortly before continueing in the loop
                time.sleep(1)

            except Exception as err:
                logging.error("Failure during loop", extra={"error": err})
                break

    # Shutdown tracker if shutdown signal is received
    except (KeyboardInterrupt, SystemExit):
        logging.info("Received shutdown signal..")


if __name__ == "__main__":
    main()
