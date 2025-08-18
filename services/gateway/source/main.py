"""
Gateway Service.
"""

# import modules
import utils.redis
import utils.config
import semver
import logging
import json
from fastapi import FastAPI, Response, status

# initialise app
app = FastAPI()


@app.get("/v1/info/{app_id}")
def read_app(app_id: int, response: Response):
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
    return {"data": info, "status": "success"}


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
