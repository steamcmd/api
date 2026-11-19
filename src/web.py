"""
Web Service and main API.
"""

# import modules
import utils.redis
import utils.steam
import config
import json
import time
import semver
import typing
import hashlib
import logging
import email.utils
from fastapi import FastAPI, Request, Response

# initialise app
app = FastAPI()


# include "pretty" for backwards compatibility
class PrettyJSONResponse(Response):
    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        # check if pretty print enabled
        if content["pretty"]:
            del content["pretty"]
            return json.dumps(content, indent=4, sort_keys=True).encode("utf-8")

        else:
            del content["pretty"]
            return json.dumps(content, sort_keys=True).encode("utf-8")


def etag_matches(header, etag):
    """
    Check if the If-None-Match header
    matches the specified ETag.
    """
    if header.strip() == "*":
        return True
    candidates = [tag.strip().removeprefix("W/") for tag in header.split(",")]
    return etag.removeprefix("W/") in candidates


def not_modified(request, etag, last_modified):
    """
    Check conditional request headers and return
    True if the client data is not modified.
    """
    if_none_match = request.headers.get("if-none-match")
    if if_none_match is not None:
        # check etag first if provided
        return etag_matches(if_none_match, etag)

    if_modified_since = request.headers.get("if-modified-since")
    if if_modified_since and last_modified is not None:
        try:
            since = email.utils.parsedate_to_datetime(if_modified_since).timestamp()
        except (TypeError, ValueError):
            return False
        return last_modified <= since

    return False


def read_last_modified(app_id):
    """
    Read last modified timestamp of app from
    cache and set it to now if not exist.
    """
    key = "modified.app." + str(app_id)
    modified = utils.redis.read(key)
    if not modified:
        utils.redis.write(key, str(int(time.time())), only_if_missing=True)
        modified = utils.redis.read(key)
    if not modified:
        return None
    try:
        return int(modified)
    except (TypeError, ValueError):
        return None


def conditional_response(request, content, last_modified=None):
    """
    Generate JSON response with ETag and Last-Modified
    headers or return 304 if not modified.
    """
    response = PrettyJSONResponse(content)
    etag = '"' + hashlib.sha1(response.body).hexdigest() + '"'

    headers = {"ETag": etag}
    if last_modified is not None:
        headers["Last-Modified"] = email.utils.formatdate(last_modified, usegmt=True)

    if not_modified(request, etag, last_modified):
        return Response(status_code=304, headers=headers)

    response.headers.update(headers)
    return response


@app.get("/v1/info/{app_id}", response_class=PrettyJSONResponse)
def read_app(request: Request, app_id: int, pretty: bool = False):
    logging.info("Requested app info", extra={"apps": str([app_id])})

    last_modified = None
    if config.cache == "True":
        info = utils.redis.read("app." + str(app_id))

        if not info:
            logging.info(
                "App info could not be found in cache", extra={"apps": str([app_id])}
            )
        else:
            info = json.loads(info)
            last_modified = read_last_modified(app_id)
            logging.info(
                "App info succesfully retrieved from cache",
                extra={"apps": str([app_id])},
            )

    else:
        info = utils.steam.get_apps_info([app_id])

    if info is None:
        logging.info(
            "The SteamCMD backend returned no actual data and failed",
            extra={"apps": str([app_id])},
        )
        # return empty result for not found app
        return {"data": {app_id: {}}, "status": "failed", "pretty": pretty}

    if not info:
        logging.info(
            "No app has been found at Steam but the request was succesfull",
            extra={"apps": str([app_id])},
        )
        # return empty result for not found app
        return {"data": {app_id: {}}, "status": "success", "pretty": pretty}

    logging.info("Succesfully retrieved app info", extra={"apps": str([app_id])})
    return conditional_response(
        request, {"data": info, "status": "success", "pretty": pretty}, last_modified
    )


@app.get("/v1/version", response_class=PrettyJSONResponse)
def read_item(pretty: bool = False):
    logging.info("Requested api version")

    # check if version succesfully read and parsed
    if config.version:
        return {
            "status": "success",
            "data": semver.parse(config.version),
            "pretty": pretty,
        }
    else:
        logging.warning(
            "No version has been defined and could therefor not satisfy the request"
        )
        return {
            "status": "error",
            "data": "Something went wrong while retrieving and parsing the current API version. Please try again later",
            "pretty": pretty,
        }


@app.get("/health")
def health_check():
    """
    Health check endpoint for Kubernetes liveness and readiness probes.
    """
    try:
        # Test Redis connection if cache is enabled
        if config.cache == "True":
            rds = utils.redis.connect()
            if rds is None:
                return {"status": "unhealthy", "error": "Redis connection failed"}, 503

            # Test Redis with a simple ping
            rds.ping()

        return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

    except Exception as e:
        logging.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}, 503


@app.get("/ready")
def readiness_check():
    """
    Readiness check endpoint for Kubernetes readiness probes.
    """
    try:
        # Test Redis connection if cache is enabled
        if config.cache == "True":
            rds = utils.redis.connect()
            if rds is None:
                return {"status": "not_ready", "error": "Redis connection failed"}, 503

            # Test Redis with a simple ping
            rds.ping()

        return {"status": "ready"}

    except Exception as e:
        logging.error(f"Readiness check failed: {e}")
        return {"status": "not_ready", "error": str(e)}, 503
