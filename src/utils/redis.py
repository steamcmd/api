import logging
import config
import redis


def connect():
    """
    Parse redis config and connect.
    """

    try:
        # try connection string, or default to separate REDIS_* env vars
        if config.redis_url:
            rds = redis.Redis.from_url(config.redis_url, db=config.redis_database_web)
            #print(rds)
            #print('----------')

        elif config.redis_password:
            rds = redis.Redis(
                host=config.redis_host,
                port=config.redis_port,
                password=config.redis_password,
                db=config.redis_database_web
            )
        else:
            rds = redis.Redis(
                host=config.redis_host,
                port=config.redis_port,
                db=config.redis_database_web
            )

    except Exception as error:
        logging.error("Failed to connect to Redis with error: " + error)
        return False

    return rds


def read(key):
    """
    Read specified key from Redis.
    """

    rds = connect()
    data = rds.get(key)

    if not data:
        return False
    data = data.decode("UTF-8")

    return data


def write(key, data):
    """
    Write specified key to Redis.
    """

    rds = connect()
    rds.set(key, data)

    return True


def remove_database_from_url(url):
    """
    Remove database if specified in the given
    connection url and return the result.
    """

    last_element = url.split('/')[-1]

    try:
        specified_database = int(last_element)
    #except TypeError:
    except ValueError:
        specified_database = 0
        print('There is no Redis database specified in the given connection string or it is not specified as an integer!')

    return url


def change_url_database(url, database):
    """
    Remove any specified database from Redis
    connection url and return edited url.
    """

    last_element = url.split('/')[-1]

    try:
        specified_database = int(last_element)
    #except TypeError:
    except ValueError:
        specified_database = 0
        print('There is no Redis database specified in the given connection string or it is not specified as an integer!')

    print(specified_database)

    #print(type(last_element))
    #if int(last_element) == int(database):


    return url