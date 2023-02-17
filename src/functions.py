"""
General Functions
"""

# import modules
import os, json, gevent, datetime, redis
from steam.client import SteamClient
from deta import Deta


def app_info(app_id):
    connect_retries = 3
    connect_timeout = 5
    current_time = str(datetime.datetime.now())

    try:
        # Sometimes it hangs for 30+ seconds. Normal connection takes about 500ms
        for _ in range(connect_retries):
            count = _ + 1
            count = str(count)

            try:
                with gevent.Timeout(connect_timeout):
                    print("Connecting via steamclient")
                    print(
                        "Retrieving app info for: "
                        + str(app_id)
                        + ", retry count: "
                        + count
                    )

                    client = SteamClient()
                    client.anonymous_login()
                    client.verbose_debug = False
                    info = client.get_product_info(apps=[app_id], timeout=1)

                    return info

            except gevent.timeout.Timeout:
                client._connecting = False

            else:
                print("Succesfully retrieved app info for app id: " + str(app_id))
                break
        else:
            raise Exception(f"Max connect retries ({connect_retries}) exceeded")

    except Exception as err:
        print("Failed in retrieving app info for app id: " + str(app_id))
        print(err)


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
        print("Incorrect set cache type: " + os.environ["CACHE_TYPE"])

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
        print("Incorrect set cache type: " + os.environ["CACHE_TYPE"])

    # return failed status
    return False


def redis_read(app_id):
    """
    Read app info from Redis cache.
    """

    # parse redis config and connect
    rds = redis.Redis(
        host=os.environ["REDIS_HOST"],
        port=os.environ["REDIS_PORT"],
        password=os.environ["REDIS_PASSWORD"],
    )

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

    except Exception as read_error:
        # print query parse error and return empty dict
        print(
            "The following error occured while trying to read and decode "
            + "from Redis cache: \n > "
            + str(read_error)
        )
        # return failed status
        return False


def redis_write(app_id, data):
    """
    Write app info to Redis cache.
    """

    # parse redis config and connect
    rds = redis.Redis(
        host=os.environ["REDIS_HOST"],
        port=os.environ["REDIS_PORT"],
        password=os.environ["REDIS_PASSWORD"],
    )

    # write cache data and set ttl
    try:
        # convert dict to json
        data = json.dumps(data)

        # insert data into cache
        rds.set(app_id, data)
        rds.expire(app_id, os.environ["CACHE_EXPIRATION"])

        # return succes status
        return True

    except Exception as redis_error:
        # print query parse error and return empty dict
        print(
            "The following error occured while trying to write to Redis cache: \n > "
            + str(redis_error)
        )

    # return fail status
    return False


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
