"""
General Functions
"""

# import modules
import utils.redis
import config
import os
import json
import gevent
import redis
import logging
from steam.client import SteamClient


def app_info(app_id):
    connect_retries = 2
    connect_timeout = 3

    logging.info("Started requesting app info", extra={"app_id": app_id})

    try:
        # Sometimes it hangs for 30+ seconds. Normal connection takes about 500ms
        for _ in range(connect_retries):
            count = str(_)

            try:
                with gevent.Timeout(connect_timeout):
                    logging.info(
                        "Retrieving app info from steamclient",
                        extra={"app_id": app_id, "retry_count": count},
                    )

                    logging.debug("Connecting via steamclient to steam api")
                    client = SteamClient()
                    client.anonymous_login()
                    client.verbose_debug = False

                    logging.debug("Requesting app info from steam api")
                    info = client.get_product_info(apps=[app_id], timeout=1)

                    return info

            except gevent.timeout.Timeout:
                logging.warning(
                    "Encountered timeout when trying to connect to steam api. Retrying.."
                )
                client._connecting = False

            else:
                logging.info("Succesfully retrieved app info", extra={"app_id": app_id})
                break
        else:
            logging.error(
                "Max connect retries exceeded",
                extra={"connect_retries": connect_retries},
            )
            raise Exception(f"Max connect retries ({connect_retries}) exceeded")

    except Exception as err:
        logging.error("Failed in retrieving app info", extra={"app_id": app_id})
        logging.error(err, extra={"app_id": app_id})


def cache_read(app_id):
    """
    Read app info from chosen cache.
    """

    if config.cache_type == "redis":
        return redis_read(app_id)
    else:
        # print query parse error and return empty dict
        logging.error(
            "Set incorrect cache type",
            extra={"app_id": app_id, "cache_type": os.environ["CACHE_TYPE"]},
        )

    # return failed status
    return False


def cache_write(app_id, data):
    """
    write app info to chosen cache.
    """

    if config.cache_type == "redis":
        return redis_write(app_id, data)
    else:
        # print query parse error and return empty dict
        logging.error(
            "Set incorrect cache type",
            extra={"app_id": app_id, "cache_type": os.environ["CACHE_TYPE"]},
        )

    # return failed status
    return False


def redis_read(app_id):
    """
    Read app info from Redis cache.
    """

    rds = utils.redis.connect()

    try:
        # get info from cache
        data = rds.get(app_id)

        # return if not found
        if not data:
            # return failed status
            return False

        # decode bytes to str
        data = data.decode("UTF-8")

        # convert json to python dict
        data = json.loads(data)

        # return cached data
        return data

    except Exception as redis_error:
        # print query parse error and return empty dict
        logging.error(
            "An error occured while trying to read and decode from Redis cache",
            extra={"app_id": app_id, "error_msg": redis_error},
        )

        # return failed status
        return False


def redis_write(app_id, data):
    """
    Write app info to Redis cache.
    """

    rds = utils.redis.connect()

    # write cache data and set ttl
    try:
        # convert dict to json
        data = json.dumps(data)

        # insert data into cache
        if int(config.cache_expiration) == 0:
            rds.set(app_id, data)

        else:
            expiration = int(config.cache_expiration)
            rds.set(app_id, data, ex=expiration)

        # return succes status
        return True

    except Exception as redis_error:
        # print query parse error and return empty dict
        logging.error(
            "An error occured while trying to write to Redis cache",
            extra={"app_id": app_id, "error_msg": redis_error},
        )

    # return fail status
    return False
