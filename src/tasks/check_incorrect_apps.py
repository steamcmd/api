from job import app, logger
from celery_singleton import Singleton
from .get_app_info import get_app_info_task
import utils.redis
import utils.steam
import config


@app.task(name="check_incorrect_apps", base=Singleton, lock_expiry=7200)
def check_incorrect_apps_task():
    """
    Check for stored apps that have the value of "false" and
    remove them from the cache. Then start tasks to retrieve
    the info for these apps.
    """

    # connecting to Redis
    rds = utils.redis.connect()

    # initialize cursor
    cursor = 0
    false_apps = []

    # use SCAN to iterate through keys that start with "app."
    while True:
        cursor, apps = rds.scan(cursor, match='app.*')
        for app in apps:
            # Check if the value of the app is "false"
            if rds.get(app) == b'false':
                app = app.decode("UTF-8")
                app = app.split(".")[1]
                false_apps.append(int(app))

        if cursor == 0:
            break

    if len(false_apps) > 0:
        logger.warning("Found " + str(len(false_apps)) + " apps that have a stored value of 'false'")

    for i in range(0, len(false_apps), config.chunk_size):
        chunk = false_apps[i : i + config.chunk_size]
        logger.warning("Deleting " + str(chunk) + " apps from cache and starting app info retrieval again")
        get_app_info_task.delay(chunk)
