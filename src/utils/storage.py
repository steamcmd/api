from job import logger
import utils.helper
import config
import logging
import os
from minio import Minio
from io import BytesIO


## meta functions


def read(path, filename):
    """
    Read file from specified directory.
    """

    match config.storage_type:
        case "local":
            response = local_read(path, filename)
        case "object":
            response = object_read(path, filename)
        case _:
            response = False

    return response


def write(content, path, filename):
    """
    Write content to file in the specified
    directory/path.
    """

    match config.storage_type:
        case "local":
            response = local_write(content, path, filename)
        case "object":
            response = object_write(content, path, filename)
        case _:
            response = False

    return response


def list(path):
    """
    List files in specified directory and return
    it as a list.
    """

    match config.storage_type:
        case "local":
            response = local_list(path)
        case "object":
            response = object_list(path)
        case _:
            response = False

    return response


## local storage functions


def local_read(path, filename):
    """
    Read file from local specified directory.
    """

    path = utils.helper.combine_paths(config.storage_directory, path)
    path = utils.helper.normalize_directory(path)
    file = path + filename

    try:
        content = open(file, "r")
        content = content.read()

    except Exception:
        logging.error("The following file could not be read: " + file)
        return False

    return content


def local_write(content, path, filename):
    """
    Write content to file to local specified
    directory.
    """

    path = utils.helper.combine_paths(config.storage_directory, path)
    path = utils.helper.normalize_directory(path)
    file = path + filename

    try:
        f = open(file, "w")
        f.write(content)
        f.close()
        logging.info("Written the following file: " + file)

    except Exception:
        logger.error("The following file could not be written locally: " + file)
        return False

    return True


def local_delete(path, filename):
    """
    Delete file in local specified directory.
    """

    path = utils.helper.combine_paths(config.storage_directory, path)
    path = utils.helper.normalize_directory(path)
    file = path + filename

    try:
        os.remove(file)
    except OSError as err:
        logging.error(
            "The following file could not be deleted locally: "
            + err.filename
            + ". The following error occured: "
            + err.strerror
        )
        return False

    return True


def local_list(path):
    """
    List files in specified local directory and
    return it as a list.
    """

    path = utils.helper.combine_paths(config.storage_directory, path)
    path = utils.helper.normalize_directory(path)

    try:
        content = os.listdir(path)

    except Exception:
        logging.error("The following directory could not be read: " + path)
        return False

    return content


## object store functions


def object_connect():
    """
    Connect to object store with credentials set
    in config environment variables.
    """

    arguments = {
        "endpoint": config.storage_object_endpoint,
        "access_key": config.storage_object_access_key,
        "secret_key": config.storage_object_secret_key,
        "secure": str(config.storage_object_secure).lower() == "true",
    }

    if config.storage_object_region:
        arguments["region"] = config.storage_object_region

    client = Minio(**arguments)

    return client


def object_read(path, filename):
    """
    Read file from object storage from specified
    directory.
    """

    file = path + filename
    conn = object_connect()

    try:
        content = conn.get_object(config.storage_object_bucket, file)

    except Exception:
        logging.error("The following file could not be retrieved: " + file)
        return False

    return content


def object_write(content, path, filename):
    """
    Write content to file to object storage in
    specified directory.
    """

    content = content.encode("utf-8")
    content = BytesIO(content)

    file = path + filename
    conn = object_connect()
    resp = conn.put_object(
        config.storage_object_bucket,
        file,
        content,
        length=-1,
        part_size=10485760,
        content_type="application/json",
    )

    return resp


def object_delete(path, filename):
    """
    Delete file in object storage specified directory.
    """

    file = path + filename
    conn = object_connect()
    resp = conn.remove_object(config.storage_object_bucket, file)

    return resp


def object_list(path, details=False):
    """
    List files in specified directory in object
    storage and return it as a list.
    """

    conn = object_connect()

    try:
        files = conn.list_objects(config.storage_object_bucket, prefix=path)
        file_list = []

        for file in files:
            file = file.object_name
            file = file.split("/")[-1]
            file_list.append(file)

    except Exception:
        logging.error("The files in following directory could not be listed: " + path)
        return False

    return file_list
