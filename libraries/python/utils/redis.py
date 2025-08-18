import utils.config as config
import logging
import redis


def connect():
    """
    Parse redis config and connect.
    """

    try:
        # Try connection string, or default to separate REDIS_* env vars
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
        logging.error(f"Failed to connect to Redis with error: {error}")
        return None

    return rds


def read(key: str):
    """
    Read specified key from Redis.
    """

    rds = connect()
    if not rds:
        return None

    try:
        # Get info from cache
        data = rds.get(key)

        # Return False if not found
        if not data:
            return None

        # Decode bytes to str
        if isinstance(data, bytes):
            data = data.decode("UTF-8")

        # Return data from Redis
        return data

    except Exception as redis_error:
        # Print query parse error and return empty dict
        logging.error(
            "An error occured while trying to read and decode from Redis",
            extra={"key": key, "error_msg": redis_error},
        )
        logging.error(redis_error)

    # Return failed status
    return None


def write(key: str, data: str | int, expiration: int = 0):
    """
    Write specified key to Redis.
    """

    rds = connect()
    if not rds:
        return None

    # Write data and set ttl
    try:
        # Insert data into Redis
        if expiration == 0:
            _ = rds.set(key, data)
        else:
            _ = rds.set(key, data, ex=expiration)

        # Return succes status
        return True

    except Exception as redis_error:
        # Print query parse error
        logging.error(
            "An error occured while trying to write to Redis cache",
            extra={"key": key, "error_msg": redis_error},
        )

    # Return fail status
    return None


def delete(key: str):
    """
    Delete specified key from Redis.
    """

    rds = connect()
    if not rds:
        return None

    # Delete specified key
    try:
        _ = rds.delete(key)

        # Return succes status
        return True

    except Exception as redis_error:
        logging.error(
            "An error occured while trying to delete a key from Redis cache",
            extra={"key": key, "error_msg": redis_error},
        )

    # Return fail status
    return None


def keys(name: str) -> list[str]:
    """
    List keys stored in Redis that optionally
    contain specified string in key name.
    """

    rds = connect()
    if not rds:
        return False

    try:
        # TODO: Write actual code in this try block instead of pseudo

        # Initialize cursor
        cursor = 0
        data_list = []

        # Use SCAN to iterate through keys
        while True:
            # Use SCAN to iterate through keys
            if not name:
                cursor, data = rds.scan(cursor)
            else:
                cursor, data = rds.scan(cursor, match=name)

            for key in data:
                data_list.append(key)

            if cursor == 0:
                return data_list

    except Exception as redis_error:
        logging.error(
            "An error occured while trying to list keys from Redis",
            extra={"error_msg": redis_error},
        )

    # Return failed status
    return None


def increment(key: str, amount: int = 1):
    """
    Increment value of amount to
    specified key to Redis.
    """

    rds = connect()
    if not rds:
        return False

    # increment data of key
    try:
        # increment and set new value
        _ = rds.incrby(key, amount)

        # return succes status
        return True

    except Exception as redis_error:
        # print query parse error and return empty dict
        logging.error(
            "An error occured while trying to increment value in Redis cache",
            extra={"key": key, "error_msg": redis_error},
        )

    # return fail status
    return None
