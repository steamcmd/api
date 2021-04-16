#!/usr/bin/env python3
"""
Main application and entrypoint.
"""

# import modules
from subprocess import check_output
import semver
import json
from urllib.parse import urlparse
import os

# import custom
import cfg as config
import vdf

# parse uri to dict
def parse_uri(uri):
    """
    Parse URI and return uri parts in a dictionary.
    """

    # split uri in parts
    uri_path = uri.split("/")

    # remove empty objects and return dict
    return list(filter(None, uri_path))


# parse query string
def query(qstring):
    """
    Parse query parameters and return dictionary.
    """

    # try parsing query string else fail
    try:

        # check for empty string of query items
        if not qstring:
            # return empty dict
            return {}

        # create default parameter dict
        pdict = {}

        # set list items in single dict
        for param in qstring.split("&"):

            # split key/value
            param = param.split("=")
            # check if both a key and value has been given
            if len(param) == 2:
                # add key/value to dict
                pdict[param[0]] = param[1]
            # check if only a has been given
            elif len(param) == 1:
                # add key and default value to dict
                pdict[param[0]] = "1"

        # return newly created dict
        return pdict

    except IndexError as query_error:

        # print query parse error and return empty dict
        print(
            "The following error occured while trying to parse the query string: \n > "
            + str(query_error)
        )
        return {}

    else:

        # return empty dict because something went wrong
        return {}


# method check
def method_check(method):
    """
    Check given method with allowed list and
    return boolean.
    """

    # set list of allowed methods from config
    allowed_methods = config.ALLOWED_METHODS

    # return true if allowed method
    if method in allowed_methods:
        return True

    # return false if no allowed method
    return False


# clean steam cache
def clean_appcache():
    """
    Clean local Steam appcache to avoid
    unexpected old info from Steam cache.
    """

    # set directory variables
    homedir = os.getenv("HOME")
    cachedir = homedir + "/.steam/appcache/"

    # list of cache files
    cache_files = [cachedir + "appinfo.vdf"]

    # remove cache files
    for cfile in cache_files:

        # check if file exists
        if os.path.isfile(cfile):

            # remove cache file
            os.remove(cfile)


# execute steamcmd
def steamcmd(gameid):
    """
    Execute steamcmd and return all output.
    """

    # cleanup cache files
    clean_appcache()

    # define steamcmd command
    cmd = [
        "steamcmd",
        "+login",
        "anonymous",
        "+app_info_update",
        "1",
        "+app_info_print",
        gameid,
        "+quit",
    ]
    # execute steamcmd and capture output
    out = check_output(cmd)
    # return decoded bytes to string output
    return out.decode("UTF-8")


# strip steamcmd output
def strip(output, gameid):
    """
    Strip all unnecessary steamcmd output and
    only return app_info data.
    """

    # remove steamcmd info
    output = output[output.find('"' + gameid + '"') :]
    output = "}".join(output.split("}")[:-1])
    output += "}"

    # return stripped output
    return output

# app definition
def app(env, start_response):
    """
    Main application definition and entrypoint.
    """

    # check if request method is allowed method
    if not method_check(env["REQUEST_METHOD"]):

        # set content and http status
        status_code = "405 Method Not Allowed"
        content = {
            "status": "error",
            "data": "This http method is not allowed. Please check the docs",
        }

    # execute when 'info' endpoint is used
    if parse_uri(env["PATH_INFO"])[0] == "info":

        # try converting given app id to int
        try:
            gameid = parse_uri(env["PATH_INFO"])[1]

            if gameid == "client":
                gameid = 252490 # https://steamdb.info/app/252490/

            elif gameid == "server":
                gameid = 258550 # https://steamdb.info/app/258550/

            else:
                gameid = False

        except IndexError:

            # set content and http status
            status_code = "400 Bad Request"
            content = {
                "status": "error",
                "data": "No app id has been given. Please add it to the url after /info/",
            }
            # set gameid value to False
            gameid = False

        except TypeError:

            # set content and http status
            status_code = "400 Bad Request"
            content = {
                "status": "error",
                "data": "An invalid app id has been given. Please check the value or the docs",
            }
            # set gameid value to False
            gameid = False

        except Exception as parse_error:

            # print gameid parse error
            print(
                "The following error occured while trying to parse the game id to int: \n > "
                + str(parse_error)
            )

            # set content and http status
            status_code = "400 Bad Request"
            content = {
                "status": "error",
                "data": "An unknown error occured when parsing the app id. Please try again",
            }
            # set gameid value to False
            gameid = False

        # execute and parse steamcmd
        if gameid:

            # execute steamcmd
            output = steamcmd(gameid)


            # remove steamcmd info
            data = strip(output, gameid)

            # parse vdf data
            data = vdf.read(data)

            # return status based on parse succces
            if data:

                # set content and http status
                status_code = "200 OK"
                content = {"status": "success", "data": data}
            else:

                # set content and http status
                status_code = "500 Internal Server Error"
                content = {
                    "status": "error",
                    "data": "Something went wrong while parsing the app info from Steam. Please try again later",
                }

    # parse query parameters
    parameters = query(env["QUERY_STRING"])

    # decode to json
    content = json.dumps(content)

    # decode to bytes
    data = content.encode("UTF-8")

    # convert allowed methods list to string
    allowed_methods = " ".join(config.ALLOWED_METHODS)

    # set list of headers
    headers = [
        ("Access-Control-Allow-Origin", "*"),
        ("Access-Control-Allow-Methods", allowed_methods),
        ("Content-Type", "application/json"),
        ("Content-Length", str(len(data))),
    ]

    # construct http response
    start_response(status_code, headers)

    # return json response
    return [data]
