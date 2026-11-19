import logging
import config
import redis
from redis.connection import ConnectionPool
import threading

# Global connection pool - thread-safe singleton
_connection_pool = None
_pool_lock = threading.Lock()


def get_connection_pool():
    """
    Get or create Redis connection pool (thread-safe singleton).
    """
    global _connection_pool

    if _connection_pool is None:
        with _pool_lock:
            if _connection_pool is None:
                try:
                    # Connection pool configuration
                    pool_kwargs = {
                        "max_connections": 50,
                        "retry_on_timeout": True,
                        "socket_connect_timeout": 5,
                        "socket_timeout": 5,
                        "health_check_interval": 30,
                    }

                    # try connection string, or default to separate REDIS_* env vars
                    if config.redis_url:
                        _connection_pool = ConnectionPool.from_url(
                            config.redis_url, db=config.redis_database, **pool_kwargs
                        )
                    elif config.redis_password:
                        _connection_pool = ConnectionPool(
                            host=config.redis_host,
                            port=config.redis_port,
                            password=config.redis_password,
                            db=config.redis_database,
                            **pool_kwargs,
                        )
                    else:
                        _connection_pool = ConnectionPool(
                            host=config.redis_host,
                            port=config.redis_port,
                            db=config.redis_database,
                            **pool_kwargs,
                        )

                    logging.info("Redis connection pool created successfully")

                except Exception as error:
                    logging.error(f"Failed to create Redis connection pool: {error}")
                    return None

    return _connection_pool


def connect():
    """
    Get Redis connection from pool.
    """
    pool = get_connection_pool()
    if pool is None:
        return None

    try:
        return redis.Redis(connection_pool=pool)
    except Exception as error:
        logging.error(f"Failed to get Redis connection from pool: {error}")
        return None


def read(key):
    """
    Read specified key from Redis.
    """
    rds = connect()

    if rds is None:
        logging.error(f"Failed to get Redis connection for key: {key}")
        return False

    try:
        # get info from cache with timeout
        data = rds.get(key)

        # return False if not found
        if not data:
            return False

        # decode bytes to str
        data = data.decode("UTF-8")

        # return data from Redis
        return data

    except redis.ConnectionError as conn_error:
        logging.error(
            f"Redis connection error while reading key {key}: {conn_error}",
            extra={"key": key, "error_type": "connection_error"},
        )
        return False
    except redis.TimeoutError as timeout_error:
        logging.error(
            f"Redis timeout error while reading key {key}: {timeout_error}",
            extra={"key": key, "error_type": "timeout_error"},
        )
        return False
    except Exception as redis_error:
        logging.error(
            f"Unexpected error while reading from Redis key {key}: {redis_error}",
            extra={
                "key": key,
                "error_type": "unexpected_error",
                "error_msg": str(redis_error),
            },
        )
        return False


def write(key, data, only_if_missing=False):
    """
    Write specified key to Redis. When only_if_missing
    is set, an existing key is left untouched.
    """
    rds = connect()

    if rds is None:
        logging.error(f"Failed to get Redis connection for key: {key}")
        return False

    # write data and set ttl
    try:
        expiration = int(config.cache_expiration)

        # insert data into Redis
        if expiration == 0:
            rds.set(key, data, nx=only_if_missing)
        else:
            rds.set(key, data, ex=expiration, nx=only_if_missing)

        # return success status
        return True

    except redis.ConnectionError as conn_error:
        logging.error(
            f"Redis connection error while writing key {key}: {conn_error}",
            extra={"key": key, "error_type": "connection_error"},
        )
        return False
    except redis.TimeoutError as timeout_error:
        logging.error(
            f"Redis timeout error while writing key {key}: {timeout_error}",
            extra={"key": key, "error_type": "timeout_error"},
        )
        return False
    except Exception as redis_error:
        logging.error(
            f"Unexpected error while writing to Redis key {key}: {redis_error}",
            extra={
                "key": key,
                "error_type": "unexpected_error",
                "error_msg": str(redis_error),
            },
        )
        return False


def increment(key, amount=1):
    """
    Increment value of amount to specified key in Redis.
    """
    rds = connect()

    if rds is None:
        logging.error(f"Failed to get Redis connection for key: {key}")
        return False

    # increment data of key
    try:
        # increment and set new value
        rds.incrby(key, amount)

        # return success status
        return True

    except redis.ConnectionError as conn_error:
        logging.error(
            f"Redis connection error while incrementing key {key}: {conn_error}",
            extra={"key": key, "error_type": "connection_error"},
        )
        return False
    except redis.TimeoutError as timeout_error:
        logging.error(
            f"Redis timeout error while incrementing key {key}: {timeout_error}",
            extra={"key": key, "error_type": "timeout_error"},
        )
        return False
    except Exception as redis_error:
        logging.error(
            f"Unexpected error while incrementing Redis key {key}: {redis_error}",
            extra={
                "key": key,
                "error_type": "unexpected_error",
                "error_msg": str(redis_error),
            },
        )
        return False
