from main import app, logger
from celery_singleton import Singleton
from .get_app_info import get_app_info_task
from .get_package_info import get_package_info_task
import utils.steam
import utils.redis
import config
import json


@app.task(name="check_changelist", base=Singleton, lock_expiry=10)
def check_changelist_task():
    """
    Check for app and package changes between changelists
    and start tasks to retrieve these changes.
    """

    previous_change_number = utils.redis.read("change_number")
    latest_change_number = utils.steam.get_change_number()

    if not previous_change_number:
        logger.warning("Previous changenumber could not be retrieved from Redis")
        current_state = utils.storage.read("state/", "changes.json")
        if current_state:
            content = json.loads(current_state)
            previous_change_number = content["change_number"]
        else:
            logger.warning(
                "Previous changenumber could not be retrieved from statefile in storage"
            )

    if not previous_change_number:
        utils.redis.write("change_number", latest_change_number)

    elif int(previous_change_number) == int(latest_change_number):
        logger.info(
            "The previous and current change number "
            + str(latest_change_number)
            + " are the same"
        )
        pass

    else:
        changes = utils.steam.get_changes_since_change_number(previous_change_number)

        for i in range(0, len(changes["apps"]), config.chunk_size):
            chunk = changes["apps"][i : i + config.chunk_size]
            get_app_info_task.delay(chunk)

        for i in range(0, len(changes["packages"]), config.chunk_size):
            chunk = changes["packages"][i : i + config.chunk_size]
            get_package_info_task.delay(chunk)

        utils.redis.write("change_number", latest_change_number)

        content = {
            "changed_apps": len(changes["apps"]),
            "changed_packages": len(changes["packages"]),
            "change_number": latest_change_number,
        }
        content = json.dumps(content)
        utils.storage.write(content, "state/", "changes.json")
