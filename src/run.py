#!/usr/bin/env python3
"""
Main application and entrypoint.
"""

# import modules
import subprocess
import re
import semver
import json
import redis
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


# api version check
def version_check(version):
    """
    Check given version and return boolean.
    """

    # list of allowed versions
    allowed_versions = config.ALLOWED_VERSIONS

    # return true if allowed version
    if version in allowed_versions:
        return True

    # return false if no allowed version
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

    # start steamcmd subprocess with stdout/stdin piped
    proc = subprocess.Popen(
        [
            "steamcmd",
            "+login",
            "anonymous",
            "+app_info_update",
            "1",
            "+app_info_print",
            gameid,
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # read stdout until we see the input prompt "Steam>"
    for line in iter(proc.stdout.readline, ""):
        # This  triggers the Steam> prompt to enter a newline so we can check for it with readline.
        proc.stdin.write(b"\n")
        proc.stdin.flush()
        if "Steam>" in line.decode("utf-8"):
            break

    # Send request for app_info_print to stdin
    app_info_print = "app_info_print " + gameid + "\n"
    proc.stdin.write(app_info_print.encode())
    proc.stdin.flush()
    output = b""
    # Format of a valid fulfilled response:
    valid_result = re.compile(", change number : [1-9]")
    # Continiously request app_info_print gameid until we see a valid response.
    while not re.search(valid_result, output.decode("utf-8")):
        for line in iter(proc.stdout.readline, ""):
            output = output + line
            if "Steam>" in line.decode("utf-8"):
                proc.stdin.write(app_info_print.encode())
                proc.stdin.flush()
                break
            # Send newline to stdin to see if the "Steam>" prompt is present
            proc.stdin.write(b"\n")
            proc.stdin.flush()
    # Get the output one last time cleanly
    proc.stdin.write(app_info_print.encode())
    proc.stdin.flush()

    output = b""
    for line in iter(proc.stdout.readline, ""):
        proc.stdin.write(b"\n")
        proc.stdin.flush()
        if "Steam>" in line.decode("utf-8"):
            break
        output = output + line

    # Close steamcmd and return output
    proc.stdin.write(b"quit")
    proc.stdin.flush()
    proc.stdin.close()
    proc.terminate()
    proc.wait(timeout=0.2)

    return output.decode("UTF-8")


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


# check current version
def parse_version():
    """
    Read and return current application version.
    """

    # read version file or set default
    try:
        # open and read version file
        version_file = open(config.VERSION_FILE, "r")
        version = version_file.read()

        # strip whitespace and newlines
        version = version.rstrip()
        # parse through semver and return version
        return semver.parse(version)

    except FileNotFoundError:
        # print error
        print("Version file ('" + config.VERSION_FILE + "') not found!")
        # return default False when error
        return False

    except ValueError as parse_error:
        # print error
        print(
            "Incorrect version used. Use the semver syntax. Received following error: \n > "
            + str(parse_error)
        )
        # return default False when error
        return False


# construct redis config
def redis_config():
    """
    Read and set Redis configuration
    from enviroment variables.
    """

    # initialize config dict
    cdict = {}

    # check for required env vars
    if os.environ.get("REDIS_TLS_URL"):
        # parse config url
        url = urlparse(os.environ.get("REDIS_TLS_URL"))

        # set configuration in dict
        cdict["host"] = url.hostname
        cdict["port"] = url.port
        cdict["ssl"] = True
        cdict["timeout"] = config.REDIS_DEFAULT_TIMEOUT
        cdict["username"] = url.username
        cdict["password"] = url.password

    elif os.environ.get("REDIS_URL"):
        # parse config url
        url = urlparse(os.environ.get("REDIS_URL"))

        # set configuration in dict
        cdict["host"] = url.hostname
        cdict["port"] = url.port
        cdict["ssl"] = False
        cdict["timeout"] = config.REDIS_DEFAULT_TIMEOUT
        cdict["username"] = url.username
        cdict["password"] = url.password

    elif os.environ.get("REDIS_HOST"):
        # set configuration in dict
        cdict["host"] = os.environ.get("REDIS_HOST")

        # check for optional port env
        if os.environ.get("REDIS_PORT"):
            # set configuration in dict
            cdict["port"] = os.environ.get("REDIS_PORT")
        else:
            # set default configuration in dict
            cdict["port"] = config.REDIS_DEFAULT_PORT

        # check for optional ssl env
        if os.environ.get("REDIS_SSL"):
            # set configuration in dict
            cdict["ssl"] = True
        else:
            # set default configuration in dict
            cdict["ssl"] = config.REDIS_DEFAULT_SSL

        # check for optional timeout env
        if os.environ.get("REDIS_TIMEOUT"):
            # set configuration in dict
            cdict["timeout"] = os.environ.get("REDIS_TIMEOUT")
        else:
            # set default configuration in dict
            cdict["timeout"] = config.REDIS_DEFAULT_TIMEOUT

        # check for optional username env
        if os.environ.get("REDIS_USERNAME"):
            # set configuration in dict
            cdict["username"] = os.environ.get("REDIS_USERNAME")
        else:
            # set default configuration in dict
            cdict["username"] = ""

        # check for optional password env
        if os.environ.get("REDIS_PASSWORD"):
            # set configuration in dict
            cdict["password"] = os.environ.get("REDIS_PASSWORD")
        else:
            # set default configuration in dict
            cdict["password"] = ""

    else:
        # set failed response
        cdict = False

    # return constructed dict
    return cdict


# test redis connection
def redis_test(redis_config):
    """
    Test Redis connection with dict config.
    """

    # parse redis config and connect
    try:
        # start redis connection
        rds = redis.Redis(
            host=redis_config["host"],
            port=redis_config["port"],
            ssl=redis_config["ssl"],
            username=redis_config["username"],
            password=redis_config["password"],
            socket_timeout=redis_config["timeout"],
        )
        # basic redis ping test
        rds.ping()
        # return redis available status
        return True

    except Exception as redis_error:
        # print query parse error and return empty dict
        print(
            "The following error occured while trying to connect to Redis: \n > "
            + str(redis_error)
        )

    # return redis available status
    return False


def cache_read(gameid):
    """
    Read app info from cache.
    """

    # parse redis config and connect
    cfg = redis_config()
    rds = redis.Redis(
        host=cfg["host"],
        port=cfg["port"],
        ssl=cfg["ssl"],
        username=cfg["username"],
        password=cfg["password"],
        socket_timeout=cfg["timeout"],
    )

    try:
        # get info from cache
        data = rds.get(gameid)

        # return if not found
        if not data:
            # return failed status
            return False

        # decode bytes to str
        data = data.decode("UTF-8")

        # return cached data
        return data

    except Exception as read_error:
        # print query parse error and return empty dict
        print(
            "The following error occured while trying to read and decode "
            + "from Redis cache: \n > "
            + str(read_error)
        )
        # return failed status
        return False


def cache_write(gameid, data, expiration=config.CACHE_EXPIRATION):
    """
    Write app info to cache.
    """

    # parse redis config and connect
    cfg = redis_config()
    rds = redis.Redis(
        host=cfg["host"],
        port=cfg["port"],
        ssl=cfg["ssl"],
        username=cfg["username"],
        password=cfg["password"],
        socket_timeout=cfg["timeout"],
    )

    # write cache data and set ttl
    try:
        rds.set(gameid, data)
        rds.expire(gameid, expiration)

        # return succes status
        return True

    except Exception as redis_error:
        # print query parse error and return empty dict
        print(
            "The following error occured while trying to write to Redis cache: \n > "
            + str(redis_error)
        )

    # return fail status
    return False


# app definition
def app(env, start_response):
    """
    Main application definition and entrypoint.
    """

    # read redis config
    rds_config = redis_config()
    # only run test if config is set
    if rds_config:
        # test redis connection
        rds_available = redis_test(rds_config)
    else:
        # test redis connection
        rds_available = False

    # check if request method is allowed method
    if not method_check(env["REQUEST_METHOD"]):

        # set content and http status
        status_code = "405 Method Not Allowed"
        content = {
            "status": "error",
            "data": "This http method is not allowed. Please check the docs",
        }

    # check if proper version and endpoint is given
    elif (
        not len(parse_uri(env["PATH_INFO"])) >= 2
        or not parse_uri(env["PATH_INFO"])[0] in config.ALLOWED_VERSIONS
        or not parse_uri(env["PATH_INFO"])[1] in config.AVAILABLE_ENDPOINTS
    ):

        # set content and http status
        status_code = "400 Bad Request"
        content = {
            "status": "error",
            "data": "Incorrect version and/or endpoint used. Please check the docs",
        }

    # execute when 'info' endpoint is used
    elif parse_uri(env["PATH_INFO"])[1] == "info":

        # try converting given app id to int
        try:
            # set gameid variable
            gameid = parse_uri(env["PATH_INFO"])[2]
            # check if gameid is integer
            float(gameid).is_integer()

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

            # read cache if redis is available
            if rds_available:
                # check and retrieve cached data
                cache_data = cache_read(gameid)

            # update and return data
            if rds_available and cache_data:
                # encode data to json
                cache_data = json.loads(cache_data)

                # set content and http status
                status_code = "200 OK"
                content = {"status": "success", "data": cache_data}

            else:
                # execute steamcmd
                output = steamcmd(gameid)

                # set and check for not found error
                error_search = "No app info for AppID " + gameid + " found"

                # set 404 error if error appeared in output
                if error_search in output:

                    # set content and http status
                    status_code = "404 Not Found"
                    content = {
                        "status": "error",
                        "data": "No information for this specific app id "
                        "could be found on Steam",
                    }

                # parse steamcmd output to json
                else:

                    # remove steamcmd info
                    data = strip(output, gameid)

                    # parse vdf data
                    data = vdf.read(data)

                    # write cache if redis is available
                    if rds_available:
                        # write data to cache
                        write_status = cache_write(gameid, json.dumps(data))

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

    elif parse_uri(env["PATH_INFO"])[1] == "version":

        # read and parse version from file
        version_semver = parse_version()

        # check if version succesfully read and parsed
        if version_semver:

            # set content and http status
            status_code = "200 OK"
            content = {"status": "success", "data": version_semver}
        else:

            # set content and http status
            status_code = "500 Internal Server Error"
            content = {
                "status": "error",
                "data": "Something went wrong while retrieving and parsing the current API version. Please try again later",
            }

    # parse query parameters
    parameters = query(env["QUERY_STRING"])

    # check if pretty print enabled
    if "pretty" in parameters and parameters["pretty"] == "1":

        # decode to json and pretty print
        content = json.dumps(content, indent=4, sort_keys=True)

    else:
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
