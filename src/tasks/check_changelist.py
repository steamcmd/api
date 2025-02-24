from job import app, logger
from celery_singleton import Singleton
from .get_app_info import get_app_info_task
from .get_package_info import get_package_info_task
import utils.steam
import utils.redis
import logging
import config
import json
import time


@app.task(name="check_changelist", base=Singleton, lock_expiry=10)
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
        changes = utils.steam.get_changes_since_change_number(previous_change_number)

        while not changes:
            changes = utils.steam.get_changes_since_change_number(
                previous_change_number
            )
            time.sleep(1)

        for i in range(0, len(changes["apps"]), config.chunk_size):
            chunk = changes["apps"][i : i + config.chunk_size]
            get_app_info_task.delay(chunk)

        # for i in range(0, len(changes["packages"]), config.chunk_size):
        #    chunk = changes["packages"][i : i + config.chunk_size]
        #    get_package_info_task.delay(chunk)

        utils.redis.write("_state.change_number", latest_change_number)
        utils.redis.increment("_state.changed_apps", len(changes["apps"]))
        utils.redis.increment("_state.changed_packages", len(changes["packages"]))
