import utils.steam
import utils.redis
import logging
from steam.client import SteamClient


def main(client: SteamClient):
    """
    Get list of available apps from Steam and compare
    it with the stored apps. Wherenecessary removes
    apps from cache or starts app info retrievals.
    """

    print("test")

    _ = client
    steam_app_list = utils.steam.get_app_list()
    cache_app_list = utils.redis.keys("app.")  # TODO: fix pseudo code

    # TODO: fix pseudo code below

    # Remove apps from cache that are not available any more
    for app in cache_app_list:
        if app not in steam_app_list:
            utils.redis.delete(app)
            logging.info(
                "Deleted app info in cache. Not available in Steam",
                extra={"app": app, "task": "compare"},
            )

    # Request app information for apps that are missing in cache
    for app in steam_app_list:
        if app not in cache_app_list:
            utils.rabbitmq.message("info", {"id": app})
            logging.info(
                "Requested app info. Missing from cache",
                extra={"app": app, "task": "compare"},
            )
