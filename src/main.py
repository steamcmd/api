"""
Main application and entrypoint.
"""

# import modules
from deta import Deta
from typing import Union
from fastapi import FastAPI, Response, status
from functions import app_info, cache_read, cache_write, log_level
import os, datetime, json, semver, typing, logging, logfmter
from logfmter import Logfmter

# load configuration
from dotenv import load_dotenv
load_dotenv()

# initialise app
app = FastAPI()

# set logformat
formatter = Logfmter(
    keys=["level"],
    mapping={"level": "levelname"}
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logging.basicConfig(handlers=[handler])

if "LOG_LEVEL" in os.environ:
    log_level(os.environ["LOG_LEVEL"])

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

    if "CACHE" in os.environ and os.environ["CACHE"]:
        info = cache_read(app_id)

        if not info:
            logging.info("App info could not be found in cache", extra={"app_id": app_id})
            info = app_info(app_id)
            cache_write(app_id, info)
        else:
            logging.info("App info was succesfully retrieved from cache", extra={"app_id": app_id})

    else:
        info = app_info(app_id)

    if not info["apps"]:
        logging.info("No app has been found at Steam but the request was succesfull", extra={"app_id": app_id})
        # return empty result for not found app
        return {"data": {app_id: {}}, "status": "success", "pretty": pretty}

    logging.info("Succesfully retrieved app info", extra={"app_id": app_id})
    return {"data": info["apps"], "status": "success", "pretty": pretty}


@app.get("/v1/version", response_class=PrettyJSONResponse)
def read_item(pretty: bool = False):
    logging.info("Requested api version")

    # check if version succesfully read and parsed
    if "VERSION" in os.environ and os.environ["VERSION"]:
        return {
            "status": "success",
            "data": semver.parse(os.environ["VERSION"]),
            "pretty": pretty,
        }
    else:
        logging.warning("No version has been defined and could therefor not satisfy the request")
        return {
            "status": "error",
            "data": "Something went wrong while retrieving and parsing the current API version. Please try again later",
            "pretty": pretty,
        }
