import logging
import sys
import os
import importlib


def list_tasks():
    """
    List Python files in local tasks directory
    and return tuple of these files. If dir not
    exists, return empty tuple.
    """

    tasks_tuple = ()
    tasks_directory = normalize_directory("tasks")

    if not os.path.exists(tasks_directory):
        return tasks_tuple

    for task in os.listdir(tasks_directory):
        if os.path.splitext(task)[1] == ".py":
            tasks_tuple = tasks_tuple + ("tasks." + os.path.splitext(task)[0],)

    return tasks_tuple


def read_env(
    key: str,
    default: str | None = None,
    choices: list[str] | None = None,
    dependency: dict[str, str] | None = None,
) -> str | None:
    """
    Get value from environment variable and return
    None if not exist. Optionally checks if other
    required variables are set.
    """

    try:
        value = os.environ[key]
        if choices and value not in choices:
            logging.critical(
                "The value '"
                + str(value)
                + "' of variable '"
                + str(key)
                + "' is incorrect and can only be set to one of the these values: "
                + str(choices)
            )
            sys.exit(1)

    except KeyError:
        if default:
            value = default
        else:
            value = None

        if dependency:
            for dep in dependency:
                if read_env(dep) == dependency[dep]:
                    logging.critical(
                        "The variable '"
                        + str(key)
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


def normalize_directory(path: str):
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


def import_tasks():
    """
    Dynamically import all task modules from the tasks
    directory. Returns a list of imported task modules.
    """

    task_modules = []
    tasks_directory = normalize_directory("tasks")

    if os.path.exists(tasks_directory):
        for file in os.listdir(tasks_directory):
            if file.endswith(".py") and file != "__init__.py":
                module_name = file[:-3]  # Remove .py extension
                task_modules.append(importlib.import_module(f"tasks.{module_name}"))

    return task_modules
