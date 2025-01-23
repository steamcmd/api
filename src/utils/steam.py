from main import logger
from steam.client import SteamClient
import requests


def init_client():
    """
    Initialize Steam client, login and
    return the client.
    """

    client = SteamClient()
    client.anonymous_login()
    client.verbose_debug = False

    return client


def get_app_list():
    """
    Get list of id's of all current apps in
    Steam and return them in a flat list.
    """

    response = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2/")
    response_json = response.json()

    apps = []
    if response.status_code != 200:
        logger.error("The Steam GetAppList API endpoint returned a non-200 http code")

    else:
        for app in response_json["applist"]["apps"]:
            apps.append(app["appid"])

    return apps


def get_change_number():
    """
    Get and return the latest change number.
    """

    client = init_client()
    info = client.get_changes_since(1, app_changes=False, package_changes=False)
    change_number = info.current_change_number

    return change_number


def get_changes_since_change_number(change_number):
    """
    Get and return lists of changed apps and
    packages since the specified change number.
    """

    client = init_client()
    info = client.get_changes_since(
        int(change_number), app_changes=True, package_changes=True
    )

    app_list = []
    if info.app_changes:
        for app in info.app_changes:
            app_list.append(app.appid)

    package_list = []
    if info.package_changes:
        for package in info.package_changes:
            package_list.append(package.packageid)

    changes = {"apps": app_list, "packages": package_list}

    return changes


def get_apps_info(apps=[]):
    """
    Get product info for list of apps and
    return the output untouched.
    """

    try:
        client = init_client()
        info = client.get_product_info(apps=apps, timeout=5)
        info = info["apps"]
    except Exception as err:
        logger.error(
            "Something went wrong while querying product info for apps: " + str(apps)
        )
        logger.error(err)
        return False

    return info


def get_packages_info(packages=[]):
    """
    Get product info for list of packages and
    return the output untouched.
    """

    try:
        client = init_client()
        info = client.get_product_info(packages=packages, timeout=5)
        info = info["packages"]
    except Exception as err:
        logger.error(
            "Something went wrong while querying product info for packages: "
            + str(packages)
        )
        logger.error(err)
        return False

    return info
