from job import app
from celery_singleton import Singleton
from .get_app_info import get_app_info_task
import utils.steam
import utils.redis
import logging
import config
import time


@app.task(name="check_changelist", base=Singleton, lock_expiry=60)
def check_changelist_task():
    """
    Check for app and package changes between changelists
    and start tasks to retrieve these changes.
    """

    previous_change_number = utils.redis.read("_state.change_number")
    latest_change_number = utils.steam.get_change_number()

    if not previous_change_number:
        logging.warning("Previous changenumber could not be retrieved from Redis")
        utils.redis.write("_state.change_number", latest_change_number)

    elif not latest_change_number:
        logging.error(
            "The current change number could not be retrieved. Instead got: "
            + str(latest_change_number)
        )
        pass

    elif int(previous_change_number) == int(latest_change_number):
        logging.info(
            "The previous and current change number "
            + str(latest_change_number)
            + " are the same"
        )
        pass

    else:
        logging.info(
            "The changenumber has been updated from "
            + str(previous_change_number)
            + " to "
            + str(latest_change_number)
        )
        # retry limited amount of times to avoid deadlocks
        changes = False
        for _ in range(config.changes_retries):
            changes = utils.steam.get_changes_since_change_number(
                previous_change_number
            )
            if changes:
                break
            time.sleep(1)

        if not changes:
            logging.error(
                "Could not retrieve changes since change number "
                + str(previous_change_number)
                + ". Retrying on the next run"
            )
            return

        for i in range(0, len(changes["apps"]), config.chunk_size):
            chunk = changes["apps"][i : i + config.chunk_size]
            get_app_info_task.delay(chunk)

        utils.redis.write("_state.change_number", latest_change_number)
        utils.redis.increment("_state.changed_apps", len(changes["apps"]))
        utils.redis.increment("_state.changed_packages", len(changes["packages"]))
