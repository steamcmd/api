"""
Gateway Service.
"""

# import modules
import utils.redis
import utils.config
import semver
import logging
import hashlib
import json
import time
import email.utils
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse

# initialise app
app = FastAPI()


def etag_matches(header: str, etag: str) -> bool:
    """
    Check if the If-None-Match header
    matches the specified ETag.
    """

    if header.strip() == "*":
        return True
    candidates = [tag.strip().removeprefix("W/") for tag in header.split(",")]
    return etag.removeprefix("W/") in candidates


def not_modified(request: Request, etag: str, last_modified: int | None) -> bool:
    """
    Check conditional request headers and return
    True if the client data is not modified.
    """

    # Check ETag first if provided
    if_none_match = request.headers.get("if-none-match")
    if if_none_match is not None:
        return etag_matches(if_none_match, etag)

    if_modified_since = request.headers.get("if-modified-since")
    if if_modified_since and last_modified is not None:
        try:
            since = email.utils.parsedate_to_datetime(if_modified_since).timestamp()
        except (TypeError, ValueError):
            return False
        return last_modified <= since

    return False


def read_last_modified(app_id: int) -> int | None:
    """
    Read last modified timestamp of app from
    cache and set it to now if not exist.
    """

    key = "modified.app." + str(app_id)
    modified = utils.redis.read(key)
    if not modified:
        _ = utils.redis.write(key, str(int(time.time())), only_if_missing=True)
        modified = utils.redis.read(key)
    if not modified:
        return None

    try:
        return int(modified)
    except (TypeError, ValueError):
        return None


def conditional_response(
    request: Request, content: dict, last_modified: int | None
) -> Response:
    """
    Generate JSON response with ETag and Last-Modified
    headers or return 304 if not modified.
    """

    response = JSONResponse(content)
    etag = '"' + hashlib.sha1(response.body).hexdigest() + '"'

    headers = {"ETag": etag}
    if last_modified is not None:
        headers["Last-Modified"] = email.utils.formatdate(last_modified, usegmt=True)

    if not_modified(request, etag, last_modified):
        return Response(status_code=304, headers=headers)

    response.headers.update(headers)
    return response


@app.get("/v1/info/{app_id}")
def read_app(request: Request, app_id: int, response: Response):
    logging.info("Requested app info", extra={"apps": str([app_id])})

    info = utils.redis.read("app." + str(app_id))

    if not info:
        logging.info(
            "App info could not be found in cache", extra={"apps": str([app_id])}
        )
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"data": {app_id: {}}, "status": "success"}

    try:
        info = json.loads(info)
    except Exception as err:
        logging.error(
            "Failed to parse cached app information to JSON",
            extra={"apps": str([app_id]), "error": err},
        )
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"data": {app_id: {}}, "status": "failed"}

    # Return app info from cache
    return conditional_response(
        request, {"data": info, "status": "success"}, read_last_modified(app_id)
    )


@app.get("/v1/version")
def read_item():
    logging.info("Requested api version")

    # Check if version succesfully read and parsed
    if utils.config.version:
        return {"status": "success", "data": semver.parse(utils.config.version)}

    logging.warning(
        "No version has been defined and could therefor not satisfy the request"
    )
    return {
        "status": "error",
        "data": "Something went wrong while retrieving and parsing the current API version. Please try again later",
    }
