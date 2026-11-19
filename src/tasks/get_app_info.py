from job import app, logger
import utils.storage
import utils.steam
import utils.redis
import json
import time


@app.task(
    name="get_app_info",
    time_limit=15,
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

    if apps is False:
        raise Exception("Retrieving app info from Steam failed")

    for app_obj in apps:
        key = "app." + str(app_obj)
        modified_key = "modified." + key
        content = {app_obj: apps[app_obj]}
        content = json.dumps(content)

        # keep previous timestamp if content not changed
        modified = None
        if utils.redis.read(key) == content:
            modified = utils.redis.read(modified_key)
        if not modified:
            modified = str(int(time.time()))

        utils.redis.write(key, content)
        utils.redis.write(modified_key, modified)
