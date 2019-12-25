#!/usr/bin/env python3
"""
Valve key/value manipulation functions.
"""

# imports
import sys
import shlex
import json


def surround_quotes(obj):
    """
    Surround input (string)
    with double quotes.
    """

    # add double quotes around string
    obj = "\"" + obj + "\""

    # return quoted string
    return obj


def read(data):
    """
    Parent function to call Valve key/value
    format read function.
    """

    # parse and return valve key/value data
    try:
        data = read_json_method(data)
    except:
        try:
            data = read_dict_method(data)
        except:
            data = False

    # return parsed data or False bool
    return data


def read_json_method(data):
    """
    Reformatting Valve key/value format
    to JSON and returning JSON.
    """

    # default vars
    parent = []
    depth = 0
    vdict = {}

    # init json and add opening bracket
    vjson = "{"

    # split into lines
    data = data.splitlines()

    # loop through vdf
    for index, line in enumerate(data):

        # split line string
        split = shlex.split(line)
        count = len(split)

        # set key vars
        key = split[0]

        # error if unexpected word count of current line
        if count > 2:
            print(
                "The line: "
                + line
                + " contains an invalid number of words. This must be 1 or 2!"
            )
            sys.exit(1)

        # parse next line if not last line
        if index == (len(data) - 1):
            # set next to false
            nextkey = False
            # flag this line as last
            lastline = True

        else:
            # get next line
            nextline = data[index + 1]
            nextsplit = shlex.split(nextline)
            nextkey = nextsplit[0]
            # flag this line as not last
            lastline = False

        # check for object start lines
        if count == 1 and not key in ["{", "}"]:
            # add colon to define object
            line = line + " : "

        # check for closing bracket and
        if key == "}" and nextkey != "}" and not lastline:
            # add colon to define object
            line = line + ","

        # check for key value lines
        if count == 2:
            # set value var
            val = split[1]

            # add colon between key/value
            line = surround_quotes(key) + " : " + surround_quotes(val)

            # check for brackets on next line
            if not nextkey in ["{", "}"]:
                # add comma to line
                line = line + ","

        # add edited line to json dict
        vjson = vjson + line

    # add closing bracket
    vjson = vjson + "}"

    # parse json to dict
    try:
        vdict = json.loads(vjson)
    except:
        vdict = False

    return vdict


# read vdf and return dict
def read_dict_method(data):
    """
    Parse Valve key/value format
    and return dictionary.
    """

    # default vars
    parent = []
    depth = 0
    vdict = {}

    # loop through vdf
    for line in data.splitlines():

        # split line string
        split = shlex.split(line)
        count = len(split)

        # set key value vars
        key = split[0]
        if count == 2:
            val = split[1]

        # error if unexpected word count of current line
        if count > 2:
            print(
                "The line: "
                + line
                + " contains an invalid number of words. This must be 1 or 2!"
            )
            sys.exit(1)

        # increase / decrease depth to track dict level
        if key == "{":
            # increase depth
            depth += 1
        elif key == "}":
            # decrease depth
            depth -= 1
            # remove last added parent from list
            parent.pop(-1)
        else:

            # add object to dict / root level
            if depth == 0:
                # add current line
                if count == 2:
                    # add key value
                    vdict[key] = val
                if count == 1:
                    # add dict of key
                    vdict[key] = {}
                    # set key as new parent
                    parent.append(key)

            # add object to dict / first level
            if depth == 1:
                # add current line
                if count == 2:
                    # add key value
                    vdict[parent[0]][key] = val
                if count == 1:
                    # add dict of key
                    vdict[parent[0]][key] = {}
                    # set key as new parent
                    parent.append(key)

            # add object to dict / second level
            if depth == 2:
                # add current line
                if count == 2:
                    # add key value
                    vdict[parent[0]][parent[1]][key] = val
                if count == 1:
                    # add dict of key
                    vdict[parent[0]][parent[1]][key] = {}
                    # set key as new parent
                    parent.append(key)

            # add object to dict / third level
            if depth == 3:
                # add current line
                if count == 2:
                    # add key value
                    vdict[parent[0]][parent[1]][parent[2]][key] = val
                if count == 1:
                    # add dict of key
                    vdict[parent[0]][parent[1]][parent[2]][key] = {}
                    # set key as new parent
                    parent.append(key)

            # add object to dict / fourth level
            if depth == 4:
                # add current line
                if count == 2:
                    # add key value
                    vdict[parent[0]][parent[1]][parent[2]][parent[3]][key] = val
                if count == 1:
                    # add dict of key
                    vdict[parent[0]][parent[1]][parent[2]][parent[3]][key] = {}
                    # set key as new parent
                    parent.append(key)

            # add object to dict / fifth level
            if depth == 5:
                # add current line
                if count == 2:
                    # add key value
                    vdict[parent[0]][parent[1]][parent[2]][parent[3]][parent[4]][
                        key
                    ] = val
                if count == 1:
                    # add dict of key
                    vdict[parent[0]][parent[1]][parent[2]][parent[3]][parent[4]][
                        key
                    ] = {}
                    # set key as new parent
                    parent.append(key)

            # add object to dict / sixth level
            if depth == 6:
                # add current line
                if count == 2:
                    # add key value
                    vdict[parent[0]][parent[1]][parent[2]][parent[3]][parent[4]][
                        parent[5]
                    ][key] = val
                if count == 1:
                    # add dict of key
                    vdict[parent[0]][parent[1]][parent[2]][parent[3]][parent[4]][
                        parent[5]
                    ][key] = {}
                    # set key as new parent
                    parent.append(key)

            # add object to dict / seventh level
            if depth == 7:
                # add current line
                if count == 2:
                    # add key value
                    vdict[parent[0]][parent[1]][parent[2]][parent[3]][parent[4]][
                        parent[5]
                    ][key][parent[6]][key] = val
                if count == 1:
                    # add dict of key
                    vdict[parent[0]][parent[1]][parent[2]][parent[3]][parent[4]][
                        parent[5]
                    ][key][parent[6]][key] = {}
                    # set key as new parent
                    parent.append(key)

    return vdict
