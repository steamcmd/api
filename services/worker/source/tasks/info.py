import utils.steam
import utils.redis
import logging
import json
import time
from steam.client import SteamClient


def main(client: SteamClient, data: dict[str, int]):
    """
    Retrieve app information from Steam and
    store it in cache.
    """

    try:
        # Retrieve app information from Steam
        info = utils.steam.get_apps_info(client, [data["id"]])
        if not info:
            raise RuntimeError("No app info returned from Steam")

        # Keep previous timestamp if content not changed
        key = "app." + str(next(iter(info)))
        content = json.dumps(info)
        modified = None
        if utils.redis.read(key) == content:
            modified = utils.redis.read("modified." + key)
        if not modified:
            modified = str(int(time.time()))

        # Write app information to Redis cache
        utils.redis.write(key, content)
        utils.redis.write("modified." + key, modified)

        # Report succesful proces
        logging.info(
            "Succesfully retrieved Steam info and stored in cache",
            extra={"app": data["id"], "task": "info"},
        )
        return True

    except Exception as err:
        # Report failed proces
        logging.error(
            "Retrieving and storing app info failed",
            extra={"payload": data, "error": repr(err), "task": "info"},
        )
        return None
