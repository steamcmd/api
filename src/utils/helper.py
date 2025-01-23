#from main import logger
import logging
import sys
import os


def list_tasks():
    """
    List Python files in local tasks directory
    and return tuple of these files.
    """

    tasks_tuple = ()
    tasks_directory = normalize_directory("tasks")
    for task in os.listdir(tasks_directory):
        if os.path.splitext(task)[1] == ".py":
            tasks_tuple = tasks_tuple + ("tasks." + os.path.splitext(task)[0],)

    return tasks_tuple


def read_env(name, default=False, dependency={}, choices=[]):
    """
    Get value from environment variable and return
    false if not exist. Optionally check if other
    variable exists.
    """

    try:
        value = os.environ[name]
        if choices and value not in choices:
            logger.critical(
                "The value '"
                + str(value)
                + "' of variable '"
                + str(name)
                + "' is incorrect and can only be set to one of the these values: "
                + str(choices)
            )
            sys.exit(1)

    except KeyError:
        if default:
            value = default
        else:
            value = False

        for dep in dependency:
            if read_env(dep) == dependency[dep]:
                logger.critical(
                    "The variable '"
                    + str(name)
                    + "' must be set because it is required when '"
                    + str(dep)
                    + "' is set to '"
                    + str(dependency[dep])
                    + "'"
                )
                sys.exit(1)

    return value


def combine_paths(*args):
    """
    Combine the input paths to 1 path and make sure
    it is valid by checking the slashes.
    """

    combined_path = ""
    for arg in args:
        if arg[0] == "/":
            arg = arg[1:]

        if arg[-1] != "/":
            arg = arg + "/"

        combined_path = combined_path + arg

    combined_path = combined_path.replace("//", "/")
    combined_path = combined_path.replace("///", "/")

    return combined_path


def normalize_directory(path):
    """
    Makes sure that relative paths always start from
    the root, have a full path and that all paths end
    with a "/".
    """

    if not path[0] == "/":
        root = os.getcwd()
        path = root + "/" + path

    if path[-1] != "/":
        path = path + "/"

    return path


def list_differences(list1, list2):
    """
    Return the items that are in list1 but
    not in list2.
    """

    difference = [item for item in list1 if item not in list2]

    return difference
