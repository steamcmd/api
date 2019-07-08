#!/usr/bin/env python3
"""
Valve key/value manipulation functions.
"""

# imports
import sys
import shlex

# read vdf and return dict
def read(data):
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
