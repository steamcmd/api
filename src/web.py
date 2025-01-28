"""
Main application and entrypoint.
"""

# import modules
import config
import os
import json
import semver
import typing
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Response
from functions import app_info, redis_read, redis_write

# load configuration
load_dotenv()

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


@app.get("/v1/info/{app_id}", response_class=PrettyJSONResponse)
def read_app(app_id: int, pretty: bool = False):
    logging.info("Requested app info", extra={"app_id": app_id})

    if config.cache == "True":
        info = redis_read(app_id)
        if info:
            info = json.loads(info)

        if not info:
            logging.info(
                "App info could not be found in cache", extra={"app_id": app_id}
            )
            info = app_info(app_id)
            data = json.dumps(info)
            redis_write(app_id, data)
        else:
            logging.info(
                "App info succesfully retrieved from cache",
                extra={"app_id": app_id},
            )

    else:
        info = app_info(app_id)

    if info is None:
        logging.info(
            "The SteamCMD backend returned no actual data and failed",
            extra={"app_id": app_id},
        )
        # return empty result for not found app
        return {"data": {app_id: {}}, "status": "failed", "pretty": pretty}

    if not info["apps"]:
        logging.info(
            "No app has been found at Steam but the request was succesfull",
            extra={"app_id": app_id},
        )
        # return empty result for not found app
        return {"data": {app_id: {}}, "status": "success", "pretty": pretty}

    logging.info("Succesfully retrieved app info", extra={"app_id": app_id})
    return {"data": info["apps"], "status": "success", "pretty": pretty}


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
