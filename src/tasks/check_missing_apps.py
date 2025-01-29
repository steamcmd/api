from job import app, logger
from celery_singleton import Singleton
from .get_app_info import get_app_info_task
import utils.storage
import utils.steam
import config


@app.task(name="check_missing_apps", base=Singleton, lock_expiry=7200)
def check_missing_apps_task():
    """
    Check for missing stored apps by comparing them with
    all available apps in Steam and start tasks to
    retrieve the info for the missing apps.
    """

    steam_apps = utils.steam.get_app_list()

    stored_apps = utils.storage.list("app/")
    stored_apps_list = []
    for app_obj in stored_apps:
        app_id = app_obj.split(".")[0]
        app_ext = app_obj.split(".")[1]
        if app_ext == "json":
            stored_apps_list.append(int(app_id))

    diff = utils.helper.list_differences(steam_apps, stored_apps_list)
    if len(diff) > 0:
        logger.info(
            "Compared stored apps and found " + str(len(diff)) + " missing apps"
        )

    for i in range(0, len(diff), config.chunk_size):
        chunk = diff[i : i + config.chunk_size]
        get_app_info_task.delay(chunk)
