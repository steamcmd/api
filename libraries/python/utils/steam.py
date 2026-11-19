import logging
import gevent
import requests
from steam.client import SteamClient
from steam.enums import EResult

# Set connection settings
CONNECT_RETRIES = 3
LOGIN_TIMEOUT = 45
LOGOUT_TIMEOUT = 10
REQUEST_TIMEOUT = 15


def init_client() -> SteamClient | None:
    """
    Initialize Steam client, login and
    return the client.
    """

    client = SteamClient()
    client.verbose_debug = False

    try:
        logging.info("Initializing steam client..")
        with gevent.Timeout(LOGIN_TIMEOUT):
            if not client.connect(retry=CONNECT_RETRIES):
                logging.error(
                    "Connecting to Steam failed",
                    extra={"connect_retries": CONNECT_RETRIES},
                )
                close_client(client)
                return None

            result = client.anonymous_login()

    except (Exception, gevent.Timeout) as err:
        logging.error("Initializing Steam client failed. Error: %s", repr(err))
        close_client(client)
        return None

    if result != EResult.OK:
        logging.error("Anonymous login to Steam failed. Result: %s", repr(result))
        close_client(client)
        return None

    return client


def close_client(client: SteamClient | None) -> None:
    """
    Logout and disconnect the Steam client.
    """

    if client is None:
        return

    try:
        with gevent.Timeout(LOGOUT_TIMEOUT):
            client.logout()
    except (Exception, gevent.Timeout) as err:
        logging.debug("Logging out Steam client failed. Error: %s", repr(err))

    try:
        client.disconnect()
    except Exception as err:
        logging.debug("Disconnecting Steam client failed. Error: %s", repr(err))


def is_ready(client: SteamClient | None) -> bool:
    """
    Check if the Steam client is connected
    and logged on.
    """

    return client is not None and bool(client.connected) and bool(client.logged_on)


def ensure_client(client: SteamClient | None) -> SteamClient | None:
    """
    Return the client if logged on, otherwise
    initialize and return a new client.
    """

    if is_ready(client):
        return client

    if client is not None:
        logging.warning("Steam client lost its connection. Reconnecting..")
        close_client(client)

    return init_client()


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
        with gevent.Timeout(REQUEST_TIMEOUT):
            info = client.get_changes_since(1, app_changes=False, package_changes=False)
        if info is None:
            logging.error("Retrieving change number failed. No response from Steam")
            return None
        change_number = info.current_change_number

    except (Exception, gevent.Timeout) as err:
        logging.error("Retrieving change number failed. Error: %s", repr(err))
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
        with gevent.Timeout(REQUEST_TIMEOUT):
            info = client.get_changes_since(
                previous_change_number, app_changes=True, package_changes=False
            )
        if info is None:
            logging.error(
                "Get changed apps since change number failed. No response from Steam",
                extra={"previous_change_number": previous_change_number},
            )
            return None
        app_list = []
        if info.app_changes:
            for app in info.app_changes:
                app_list.append(app.appid)

    except (Exception, gevent.Timeout) as err:
        logging.error(
            "Get changed apps since change number failed. Error: %s",
            repr(err),
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
        # Query app info with timeout
        with gevent.Timeout(REQUEST_TIMEOUT):
            info = client.get_product_info(apps=apps, timeout=3)
        if info is None:
            logging.error("Querying app info failed. Result is None")
            return None
        info = info["apps"]

    except (Exception, gevent.Timeout) as err:
        logging.error(
            "Querying app info failed. Error: %s", repr(err), extra={"apps": str(apps)}
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
