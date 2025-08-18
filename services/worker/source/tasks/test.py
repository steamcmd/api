import logging
from steam.client import SteamClient


def main(client: SteamClient):
    """
    Test task doing nothing.
    """

    logging.info("Test", extra={"foo": "bar"})
