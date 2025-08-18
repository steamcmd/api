import logging
import requests
from steam.client import SteamClient


def init_client() -> SteamClient | None:
    """
    Initialize Steam client, login and
    return the client.
    """

    try:
        logging.info("Initializing steam client..")
        client = SteamClient()
        _ = client.anonymous_login()
        _ = client.verbose_debug = False

    except Exception as err:
        logging.error("Initializing Steam client failed. Error: %s", err)
        return None

    return client


def get_app_list() -> list[int] | None:
    """
    Get list of id's of all current apps in
    Steam and return them in a flat list.
    """

    response = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2/")
    response_json = response.json()

    apps = []
    if response.status_code != 200:
        logging.error("The Steam GetAppList API endpoint returned a non-200 http code")
        return None

    else:
        for app in response_json["applist"]["apps"]:
            apps.append(app["appid"])

    return apps


def get_change_number(client: SteamClient) -> int | None:
    """
    Get and return the latest change number.
    """

    try:
        info = client.get_changes_since(1, app_changes=False, package_changes=False)
        change_number = info.current_change_number

    except Exception as err:
        logging.error("Retrieving change number failed. Error: %s", err)
        return None

    return change_number


def get_changed_apps(
    client: SteamClient, previous_change_number: int
) -> list[int] | None:
    """
    Get and return lists of changed apps since
    the specified change number.
    """

    try:
        info = client.get_changes_since(
            previous_change_number, app_changes=True, package_changes=False
        )
        app_list = []
        if info.app_changes:
            for app in info.app_changes:
                app_list.append(app.appid)

    except Exception as err:
        logging.error(
            "Get changed apps since change number failed. Error: %s",
            err,
            extra={"previous_change_number": previous_change_number},
        )
        return None

    return app_list


def get_apps_info(client: SteamClient, apps: list[int]):
    """
    Get product info for list of apps and
    return the raw output.
    """

    try:
        info = client.get_product_info(apps=apps, timeout=3)
        if info is None:
            logging.error("Querying app info failed. Result is None")
            return None
        info = info["apps"]

    except Exception as err:
        logging.error(
            "Querying app info failed. Error: %s", err, extra={"apps": str(apps)}
        )
        return None

    return info


# def get_apps_info(apps=[]):
#    """
#    Get product info for list of apps and
#    return the output untouched.
#    """
#
#    connect_retries = 2
#    connect_timeout = 3
#    client = None
#
#    logging.info("Started requesting app info", extra={"apps": str(apps)})
#
#    try:
#        # Sometimes it hangs for 30+ seconds. Normal connection takes about 500ms
#        for _ in range(connect_retries):
#            count = str(_)
#
#            try:
#                with gevent.Timeout(connect_timeout):
#                    logging.info(
#                        "Retrieving app info from steamclient",
#                        extra={"apps": str(apps), "retry_count": count},
#                    )
#
#                    client = init_client()
#
#                    logging.debug(
#                        "Requesting app info from steam api", extra={"apps": str(apps)}
#                    )
#                    info = client.get_product_info(apps=apps, timeout=1)
#                    info = info["apps"]
#
#                    client.logout()
#
#                    return info
#
#            except gevent.timeout.Timeout:
#                logging.warning(
#                    "Encountered timeout when trying to connect to steam api. Retrying.."
#                )
#                if client:
#                    client._connecting = False
#                    client.logout()
#
#            else:
#                logging.info(
#                    "Succesfully retrieved app info", extra={"apps": str(apps)}
#                )
#                break
#        else:
#            if client:
#                client._connecting = False
#                client.logout()
#            logging.error(
#                "Max connect retries exceeded",
#                extra={"apps": str(apps), "connect_retries": connect_retries},
#            )
#            raise Exception(f"Max connect retries ({connect_retries}) exceeded")
#
#    except Exception as err:
#        if client:
#            client._connecting = False
#            client.logout()
#        logging.error(
#            "Failed in retrieving app info with error: " + str(err),
#            extra={"apps": str(apps)},
#        )
#        return False
