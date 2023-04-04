"""
General Functions
"""
from gevent import monkey; monkey.patch_all()

# import modules
import os, json, gevent, datetime, redis
import requests
from steam.client import SteamClient
from deta import Deta

# setup gevent to use requests


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


def tag_info(tag_ids):
    """
    Fetch tag information from cache or steam api
    """

    response_tags = []

    # check if tag ids are in cache
    for tag_id in tag_ids:
        tag = cache_read("tag-{}".format(tag_id))

        if tag:
            response_tags.append(tag)
            tag_ids.remove(tag_id)

    # if all tags are in cache return them
    if not tag_ids:
        return response_tags
    

    # Fetch tag information from steam api
    params = {
        "language": "english",
    }

    # add tag ids to params in format of tagids[0]=1&tagids[1]=2, etc
    for i, tag_id in enumerate(tag_ids):
        params["tagids[" + str(i) + "]"] = tag_id   

    if "STEAM_API_KEY" in os.environ:
        params["key"] = os.environ["STEAM_API_KEY"]

    url = "https://api.steampowered.com/IStoreService/GetLocalizedNameForTags/v1/"

    # fetch tag information from steam api
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()

        # save each tag to the cache
        for tag in r.json()["response"]["tags"]:
            cache_write("tag-{}".format(tag["tagid"]), tag)
            response_tags.append(tag)
        
    
    except Exception as err:
        print("Error while fetching tag info for tag ids: " + ",".join(tag_ids))
        print(err)
        return False

    # return tags
    return response_tags




    

def category_info(category_ids):
    # check if category ids are in cache
    response_categories = []

    for category_id in category_ids:
        category = cache_read("category-{}".format(category_id))

        if category:
            response_categories.append(category)
            category_ids.remove(category_id)

    # if all categories are in cache return them
    if not category_ids:
        return response_categories
    

    # Fetch category information from steam api
    params = {
        "language": "english",
    }

    # fetch category info from steam api
    if "STEAM_API_KEY" in os.environ:
        params["key"] = os.environ["STEAM_API_KEY"]

    url = "https://api.steampowered.com/IStoreBrowseService/GetStoreCategories/v1/"

    # fetch category information from steam api
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()

        # save each category to the cache
        for category in r.json()["response"]["categories"]:
            cache_write("category-{}".format(category["id"]), category)
            response_categories.append(category)

    except Exception as err:
        print("Error while fetching category info for category ids: " + ",".join(category_ids))
        print(err)
        return False

    # return categories
    return response_categories






def cache_read(cache_id):
    """
    Read app info from chosen cache.
    """

    if os.environ["CACHE_TYPE"] == "redis":
        return redis_read(cache_id)
    elif os.environ["CACHE_TYPE"] == "deta":
        return deta_read(cache_id)
    else:
        # print query parse error and return empty dict
        print("Incorrect set cache type: " + os.environ["CACHE_TYPE"])

    # return failed status
    return False


def cache_write(cache_id, data):
    """
    write app info to chosen cache.
    """

    if os.environ["CACHE_TYPE"] == "redis":
        return redis_write(cache_id, data)
    elif os.environ["CACHE_TYPE"] == "deta":
        return deta_write(cache_id, data)
    else:
        # print query parse error and return empty dict
        print("Incorrect set cache type: " + os.environ["CACHE_TYPE"])

    # return failed status
    return False


def redis_connection():
    """
    Parse redis config and connect.
    """

    # try connection string, or default to separate REDIS_* env vars
    if "REDIS_URL" in os.environ:
        rds = redis.Redis.from_url(os.environ["REDIS_URL"])
    else:
        rds = redis.Redis(
            host=os.environ["REDIS_HOST"],
            port=os.environ["REDIS_PORT"],
            password=os.environ["REDIS_PASSWORD"],
        )

    # return connection
    return rds


def redis_read(cache_key):
    """
    Read app info from Redis cache.
    """

    rds = redis_connection()

    try:
        # get info from cache
        data = rds.get(cache_key)

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


def redis_write(cache_key, data):
    """
    Write app info to Redis cache.
    """

    rds = redis_connection()

    # write cache data and set ttl
    try:
        # convert dict to json
        data = json.dumps(data)

        # insert data into cache
        rds.set(cache_key, data)
        rds.expire(cache_key, os.environ["CACHE_EXPIRATION"])

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
