from main import app, logger
import utils.storage
import utils.steam
import json


@app.task(
    name="get_app_info",
    time_limit=3,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 5},
)
def get_app_info_task(apps=[]):
    """
    Get app information of input list of apps, generate
    separate json files and upload them to the store.
    """

    logger.info("Getting product info for following apps: " + str(apps))
    apps = utils.steam.get_apps_info(apps)

    for app_obj in apps:
        content = json.dumps(apps[app_obj])
        utils.storage.write(content, "app/", str(app_obj) + ".json")
