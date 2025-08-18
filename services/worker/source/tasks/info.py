import utils.steam
import utils.redis
import logging
import json
from steam.client import SteamClient


def main(client: SteamClient, data: dict[str, int]):
    """
    Retrieve app information from Steam and
    store it in cache.
    """

    try:
        # Retrieve app information from Steam
        info = utils.steam.get_apps_info(client, [data["id"]])

        # Write app information to Redis cache
        utils.redis.write("app." + str(next(iter(info))), json.dumps(info))

        # Report succesful proces
        logging.info(
            "Succesfully retrieved Steam info and stored in cache",
            extra={"app": data["id"], "task": "info"},
        )
        return True

    except Exception as err:
        # Report failed proces
        logging.info(
            "Received message from queue",
            extra={"payload": data, "error": err, "task": "info"},
        )
        return None
