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
            rds = redis.Redis.from_url(config.redis_url, db=config.redis_database)

        elif config.redis_password:
            rds = redis.Redis(
                host=config.redis_host,
                port=config.redis_port,
                password=config.redis_password,
                db=config.redis_database,
            )
        else:
            rds = redis.Redis(
                host=config.redis_host, port=config.redis_port, db=config.redis_database
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

    try:
        # get info from cache
        data = rds.get(key)

        # return False if not found
        if not data:
            return False

        # decode bytes to str
        data = data.decode("UTF-8")

        # return data from Redis
        return data

    except Exception as redis_error:
        # print query parse error and return empty dict
        logging.error(
            "An error occured while trying to read and decode from Redis",
            extra={"key": key, "error_msg": redis_error},
        )
        logging.error(redis_error)

    # return failed status
    return False


def write(key, data):
    """
    Write specified key to Redis.
    """

    rds = connect()

    # write data and set ttl
    try:
        expiration = int(config.cache_expiration)

        # insert data into Redis
        if expiration == 0:
            rds.set(key, data)
        else:
            rds.set(key, data, ex=expiration)

        # return succes status
        return True

    except Exception as redis_error:
        # print query parse error and return empty dict
        logging.error(
            "An error occured while trying to write to Redis cache",
            extra={"key": key, "error_msg": redis_error},
        )
        logging.error(redis_error)

    # return fail status
    return False


def increment(key, amount=1):
    """
    Increment value of amount to
    specified key to Redis.
    """

    rds = connect()

    # increment data of key
    try:
        # increment and set new value
        rds.incrby(key, amount)

        # return succes status
        return True

    except Exception as redis_error:
        # print query parse error and return empty dict
        logging.error(
            "An error occured while trying to increment value in Redis cache",
            extra={"key": key, "error_msg": redis_error},
        )

    # return fail status
    return False
