import gevent
import logging
import requests
from steam.client import SteamClient


def init_client():
    """
    Initialize Steam client, login and
    return the client.
    """

    logging.debug("Connecting via steamclient to steam api")
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
        logging.error("The Steam GetAppList API endpoint returned a non-200 http code")
        return False

    else:
        for app in response_json["applist"]["apps"]:
            apps.append(app["appid"])

    return apps


def get_change_number():
    """
    Get and return the latest change number.
    """

    connect_retries = 2
    connect_timeout = 3
    client = None

    try:
        # Sometimes it hangs for 30+ seconds. Normal connection takes about 500ms
        for _ in range(connect_retries):
            count = str(_)

            try:
                with gevent.Timeout(connect_timeout):

                    client = init_client()
                    info = client.get_changes_since(
                        1, app_changes=False, package_changes=False
                    )
                    change_number = info.current_change_number

                    client.logout()

                    return change_number

            except gevent.timeout.Timeout:
                if client:
                    client._connecting = False
                    client.logout()

            else:
                break
        else:
            if client:
                client._connecting = False
                client.logout()
            raise Exception(f"Max connect retries ({connect_retries}) exceeded")

    except Exception as err:
        if client:
            client._connecting = False
            client.logout()

        logging.error(
            "Encountered the following error when trying to retrieve latest change number: "
            + str(err)
        )
        return False


def get_changes_since_change_number(change_number):
    """
    Get and return lists of changed apps and
    packages since the specified change number.
    """

    connect_retries = 2
    connect_timeout = 3
    client = None

    try:
        # Sometimes it hangs for 30+ seconds. Normal connection takes about 500ms
        for _ in range(connect_retries):
            count = str(_)

            try:
                with gevent.Timeout(connect_timeout):

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

                    client.logout()

                    return changes

            except gevent.timeout.Timeout:
                if client:
                    client._connecting = False
                    client.logout()

            else:
                break
        else:
            if client:
                client._connecting = False
                client.logout()
            raise Exception(f"Max connect retries ({connect_retries}) exceeded")

    except Exception as err:
        if client:
            client._connecting = False
            client.logout()
        logging.error(
            "Failed in get changes since last change number with error: " + str(err),
            extra={"changenumber": str(change_number)},
        )
        return False


def get_apps_info(apps=[]):
    """
    Get product info for list of apps and
    return the output untouched.
    """

    connect_retries = 2
    connect_timeout = 3
    client = None

    logging.info("Started requesting app info", extra={"apps": str(apps)})

    try:
        # Sometimes it hangs for 30+ seconds. Normal connection takes about 500ms
        for _ in range(connect_retries):
            count = str(_)

            try:
                with gevent.Timeout(connect_timeout):
                    logging.info(
                        "Retrieving app info from steamclient",
                        extra={"apps": str(apps), "retry_count": count},
                    )

                    client = init_client()

                    logging.debug(
                        "Requesting app info from steam api", extra={"apps": str(apps)}
                    )
                    info = client.get_product_info(apps=apps, timeout=1)
                    info = info["apps"]

                    client.logout()

                    return info

            except gevent.timeout.Timeout:
                logging.warning(
                    "Encountered timeout when trying to connect to steam api. Retrying.."
                )
                if client:
                    client._connecting = False
                    client.logout()

            else:
                logging.info(
                    "Succesfully retrieved app info", extra={"apps": str(apps)}
                )
                break
        else:
            if client:
                client._connecting = False
                client.logout()
            logging.error(
                "Max connect retries exceeded",
                extra={"apps": str(apps), "connect_retries": connect_retries},
            )
            raise Exception(f"Max connect retries ({connect_retries}) exceeded")

    except Exception as err:
        if client:
            client._connecting = False
            client.logout()
        logging.error(
            "Failed in retrieving app info with error: " + str(err),
            extra={"apps": str(apps)},
        )
        return False


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
        logging.error(
            "Something went wrong while querying product info for packages: "
            + str(packages)
        )
        logging.error(err)
        return False

    return info
