"""
General Functions
"""

# import modules
import os, json, gevent, datetime, redis, logging
from steam.client import SteamClient
from deta import Deta


def app_info(app_id):
    connect_retries = 2
    connect_timeout = 3
    current_time = str(datetime.datetime.now())

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

    if os.environ["CACHE_TYPE"] == "redis":
        return redis_read(app_id)
    elif os.environ["CACHE_TYPE"] == "deta":
        return deta_read(app_id)
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

    if os.environ["CACHE_TYPE"] == "redis":
        return redis_write(app_id, data)
    elif os.environ["CACHE_TYPE"] == "deta":
        return deta_write(app_id, data)
    else:
        # print query parse error and return empty dict
        logging.error(
            "Set incorrect cache type",
            extra={"app_id": app_id, "cache_type": os.environ["CACHE_TYPE"]},
        )

    # return failed status
    return False


def redis_connection():
    """
    Parse redis config and connect.
    """

    # try connection string, or default to separate REDIS_* env vars
    if "REDIS_URL" in os.environ:
        rds = redis.Redis.from_url(os.environ["REDIS_URL"])
    elif "REDIS_PASSWORD" in os.environ:
        rds = redis.Redis(
            host=os.environ["REDIS_HOST"],
            port=os.environ["REDIS_PORT"],
            password=os.environ["REDIS_PASSWORD"],
        )
    else:
        rds = redis.Redis(host=os.environ["REDIS_HOST"], port=os.environ["REDIS_PORT"])

    # return connection
    return rds


def redis_read(app_id):
    """
    Read app info from Redis cache.
    """

    rds = redis_connection()

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

    rds = redis_connection()

    # write cache data and set ttl
    try:
        # convert dict to json
        data = json.dumps(data)

        # insert data into cache
        expiration = int(os.environ["CACHE_EXPIRATION"])
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


def log_level(level):
    """
    Sets lowest level to log.
    """

    match level:
        case "debug":
            logging.getLogger().setLevel(logging.DEBUG)
        case "info":
            logging.getLogger().setLevel(logging.INFO)
        case "warning":
            logging.getLogger().setLevel(logging.WARNING)
        case "error":
            logging.getLogger().setLevel(logging.ERROR)
        case "critical":
            logging.getLogger().setLevel(logging.CRITICAL)
        case _:
            logging.getLogger().setLevel(logging.WARNING)


def deta_read(app_id):
    """
    Read app info from Deta base cache.
    """

    # initialize with a project key
    deta = Deta(os.environ["DETA_PROJECT_KEY"])

    # connect (and create) database
    dbs = deta.Base(os.environ["DETA_BASE_NAME"])

    try:
        # get info from cache
        data = dbs.get(str(app_id))

        # return if not found
        if not data:
            # return failed status
            return False

        # return cached data
        return data["data"]

    except Exception as read_error:
        # print query parse error and return empty dict
        print(
            "The following error occured while trying to read and decode "
            + "from Deta cache:"
        )
        print("> " + str(read_error))

        # return failed status
        return False


def deta_write(app_id, data):
    """
    Write app info to Deta base cache.
    """

    # initialize with a project key
    deta = Deta(os.environ["DETA_PROJECT_KEY"])

    # connect (and create) database
    dbs = deta.Base(os.environ["DETA_BASE_NAME"])

    # write cache data and set ttl
    try:
        # set expiration ttl
        expiration = int(os.environ["CACHE_EXPIRATION"])

        # insert data into cache
        dbs.put({"data": data}, str(app_id), expire_in=expiration)

        # return succes status
        return True

    except Exception as write_error:
        # print query parse error and return empty dict
        print("The following error occured while trying to write to Deta cache:")
        print("> " + str(write_error))

    # return fail status
    return False
