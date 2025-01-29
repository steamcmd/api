"""
General Functions
"""

# import modules
import utils.redis
import config
import gevent
import logging
from steam.client import SteamClient


def app_info(apps=[]):
    """
    Get product info for list of apps and
    return the output untouched.
    """

    connect_retries = 2
    connect_timeout = 3

    logging.info("Started requesting app info", extra={"apps": str(apps)})

    try:
        # Sometimes it hangs for 30+ seconds. Normal connection takes about 500ms
        for _ in range(connect_retries):
            count = str(_)

            try:
                with gevent.Timeout(connect_timeout):
                    logging.info(
                        "Retrieving app info from steamclient",
                        extra={"apps": str(apps), "retry_count": count},
                    )

                    logging.debug("Connecting via steamclient to steam api")
                    client = SteamClient()
                    client.anonymous_login()
                    client.verbose_debug = False

                    logging.debug("Requesting app info from steam api", extra={"apps": str(apps)})
                    info = client.get_product_info(apps=apps, timeout=1)

                    return info

            except gevent.timeout.Timeout:
                logging.warning(
                    "Encountered timeout when trying to connect to steam api. Retrying.."
                )
                client._connecting = False

            else:
                logging.info("Succesfully retrieved app info", extra={"apps": str(apps)})
                break
        else:
            logging.error(
                "Max connect retries exceeded",
                extra={"apps": str(apps), "connect_retries": connect_retries},
            )
            raise Exception(f"Max connect retries ({connect_retries}) exceeded")

    except Exception as err:
        logging.error("Failed in retrieving app info with error: " + str(err), extra={"apps": str(apps)})
        return False

    return info

def get_apps_info(apps=[]):
    """
    Get product info for list of apps and
    return the output untouched.
    """

    try:
        client = init_client()
        info = client.get_product_info(apps=apps, timeout=5)
        info = info["apps"]
    except Exception as err:
        logger.error(
            "Something went wrong while querying product info", extra={"apps": str(apps)}
        )
        logger.error(err)
        return False

    return info