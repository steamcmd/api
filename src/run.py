#!/usr/bin/python3

# imports
from subprocess import check_output
import json
import vdf

# parse uri
def parse(uri):

    # strip first fw slash
    if uri[0] == '/':
        uri = uri[1:]

    # check if proper number
    if uri.isdigit():
        # return orignal number
        return(uri)
    else:
        # return False
        return(False)


# execute steamcmd
def steamcmd(gameid):

    # define steamcmd command
    cmd = ['steamcmd', '+login', 'anonymous', '+app_info_update', '1', '+app_info_print', gameid, '+quit']
    # execute steamcmd
    out = check_output(cmd)
    # decode bytes to string
    out = out.decode('UTF-8')

    # return steamcmd output
    return(out)


# strip steamcmd output
def strip(output, gameid):

    # remove steamcmd info
    output = output[output.find('"' + gameid + '"'):]
    output = '}'.join(output.split('}')[:-1])
    output += '}'

    # return stripped output
    return(output)


# app definition
def app(environ, start_response):

    # strip gameid from URI
    path = environ['PATH_INFO']
    gameid = parse(path)

    # execute when id is given
    if gameid:

        # execute steamcmd
        output = steamcmd(gameid)

        # set and check for not found error
        error_search = 'No app info for AppID ' + gameid + ' found'
        if error_search in output:

            # set content and http status
            status_code = '404 Not Found'
            content = {
                'status' : 'error',
                'description' : 'No information for this specific app id could be found on Steam'
            }

        else:

            # remove steamcmd info
            data = strip(output, gameid)

            # parse vdf data
            data = vdf.read(data)

            # set content and http status
            status_code = '200 OK'
            content = {
                'status' : 'success',
                'data'   : data
            }

    else:

        # set content and http status
        status_code = '422 Unprocessable Entity'
        content = {
            'status' : 'error',
            'description' : 'An invalid number has been given'
        }

    # decode to json and bytes
    data = json.dumps(content)
    data = data.encode('UTF-8')

    # construct http response2
    start_response(status_code, [
        ("Content-Type", "application/json"),
        ("Content-Length", str(len(data)))
    ])
    return iter([data])
