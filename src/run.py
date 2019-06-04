#!/usr/bin/python3
"""
Main application and entrypoint.
"""

# imports
from subprocess import check_output
import json
import vdf

# parse uri
def parse(uri):
    """
    Parse URI and return given number.
    """

    # strip first fw slash
    if uri[0] == '/':
        uri = uri[1:]

    # check if proper number
    if uri.isdigit():
        # return orignal number
        return uri

    # return False
    return False


# parse query string
def query(qstring):
    """
    Parse query parameters and return dictionary.
    """

    # try parsing query string else fail
    try:

        # create default list and dict
        plist = []
        pdict = {}

        # check if multiple key/value
        if '&' in qstring:
            # split multiple key/value
            plist = qstring.split('&')
        else:
            # set single key/value to list
            plist.append(qstring)

        # set list items in single dict
        for param in plist:

            # split key/value
            param = param.split('=')

            # add key/value to dict
            pdict[param[0]] = param[1]

    except IndexError as query_error:

        print('The following error occured while trying to parse the query string: \n > ' \
               + str(query_error))
        pdict = False

    # return parsed parameters in dict or error
    return pdict


# execute steamcmd
def steamcmd(gameid):
    """
    Execute steamcmd and return all output.
    """

    # define steamcmd command
    cmd = ['steamcmd', '+login', 'anonymous',
           '+app_info_update', '1',
           '+app_info_print', gameid,
           '+quit']
    # execute steamcmd
    out = check_output(cmd)
    # decode bytes to string
    out = out.decode('UTF-8')

    # return steamcmd output
    return out


# strip steamcmd output
def strip(output, gameid):
    """
    Strip all unnecessary steamcmd output and
    only return app_info data.
    """

    # remove steamcmd info
    output = output[output.find('"' + gameid + '"'):]
    output = '}'.join(output.split('}')[:-1])
    output += '}'

    # return stripped output
    return output


# app definition
def app(env, start_response):
    """
    Main application definition and entrypoint.
    """

    # default values
    pretty_enabled = 0

    # strip gameid from URI
    gameid = parse(env['PATH_INFO'])

    # list of allowed methods
    allowed_methods = [
        'GET',
        'HEAD',
        'OPTIONS'
    ]

    # set request method
    request_method = env['REQUEST_METHOD']

    # check if request method is GET
    if not request_method in allowed_methods:

        # set content and http status
        status_code = '405 Method Not Allowed'
        content = {
            'status' : 'error',
            'description' : 'This http method is not allowed. Please check the docs'
        }

        print('bla')

    else:

        # check if query parameters are set
        if env['QUERY_STRING'] != '':
            # parse query parameters
            parameters = query(env['QUERY_STRING'])
        else:
            # set empty dict
            parameters = {}

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
                    'description' : 'No information for this specific app id' \
                                    ' could be found on Steam'
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

        # check if pretty print enabled
        if 'pretty' in parameters:
            # try converting string to int
            try:
                # convert parameter to int
                pretty_enabled = int(parameters['pretty'])

            except ValueError:
                # set enabled to false
                pretty_enabled = 0
        else:
            # set enabled to false
            pretty_enabled = 0

    # process prettyprint
    if pretty_enabled:
        # decode to json and pretty print
        content = json.dumps(content, indent=4, sort_keys=True)

    else:
        # decode to json
        content = json.dumps(content)

    # decode to bytes
    data = content.encode('UTF-8')

    # convert allowed methods list to string
    allowed_methods = ' '.join(allowed_methods)

    # set list of headers
    headers = [
        ("Access-Control-Allow-Methods", allowed_methods),
        ("Content-Type", "application/json"),
        ("Content-Length", str(len(data)))
    ]

    # construct http response
    start_response(status_code, headers)

    # return json response
    return iter([data])
