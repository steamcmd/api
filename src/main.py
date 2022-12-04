"""
Main application and entrypoint.
"""

# import modules
from deta import Deta
from typing import Union
from fastapi import FastAPI, Response, status
from functions import app_info, cache_read, cache_write
import os, datetime, json, semver, typing

# load configuration
from dotenv import load_dotenv

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

    if os.environ["CACHE"]:
        info = cache_read(app_id)

        if not info:
            print("App info: " + str(app_id) + " could not be find in the cache")
            info = app_info(app_id)
            cache_write(app_id, info)

    else:
        info = app_info(app_id)

    if not info["apps"]:
        # return empty result for not found app
        return {"data": {app_id: {}}, "status": "success", "pretty": pretty}

    return {"data": info["apps"], "status": "success", "pretty": pretty}


@app.get("/v1/version", response_class=PrettyJSONResponse)
def read_item(pretty: bool = False):
    # check if version succesfully read and parsed
    if os.environ["VERSION"]:
        return {
            "status": "success",
            "data": semver.parse(os.environ["VERSION"]),
            "pretty": pretty,
        }
    else:
        return {
            "status": "error",
            "data": "Something went wrong while retrieving and parsing the current API version. Please try again later",
            "pretty": pretty,
        }
