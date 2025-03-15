import utils.general
import utils.helper
import logging
from dotenv import load_dotenv
from logfmter import Logfmter

# fmt: off

# Load values from .env file
load_dotenv()

# Set variables based on environment
cache = utils.helper.read_env("CACHE", "False", choices=[ "True", "False" ])
cache_type = utils.helper.read_env("CACHE_TYPE", "redis", choices=[ "redis" ])
cache_expiration = utils.helper.read_env("CACHE_EXPIRATION", "120")
 
redis_url = utils.helper.read_env("REDIS_URL")
redis_host = utils.helper.read_env("REDIS_HOST", "localhost")
redis_port = utils.helper.read_env("REDIS_PORT", "6379")
redis_password = utils.helper.read_env("REDIS_PASSWORD")
redis_database = utils.helper.read_env("REDIS_DATABASE", "0")

storage_type = utils.helper.read_env("STORAGE_TYPE", "local", choices=[ "local", "object" ])
storage_directory = utils.helper.read_env("STORAGE_DIRECTORY", "data/", dependency={ "STORAGE_TYPE": "local" })
storage_object_endpoint = utils.helper.read_env("STORAGE_OBJECT_ENDPOINT", dependency={ "STORAGE_TYPE": "object" })
storage_object_access_key = utils.helper.read_env("STORAGE_OBJECT_ACCESS_KEY", dependency={ "STORAGE_TYPE": "object" })
storage_object_secret_key = utils.helper.read_env("STORAGE_OBJECT_SECRET_KEY", dependency={ "STORAGE_TYPE": "object" })
storage_object_bucket = utils.helper.read_env("STORAGE_OBJECT_BUCKET", dependency={ "STORAGE_TYPE": "object" })
storage_object_secure = utils.helper.read_env("STORAGE_OBJECT_SECURE", True)
storage_object_region = utils.helper.read_env("STORAGE_OBJECT_REGION", False)

log_level = utils.helper.read_env("LOG_LEVEL", "info", choices=[ "debug", "info", "warning", "error", "critical" ])
version = utils.helper.read_env("VERSION", "9.9.9")

# Set general settings
chunk_size = 10

# Logging configuration
formatter = Logfmter(keys=["level"], mapping={"level": "levelname"})
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logging.basicConfig(handlers=[handler], level=utils.general.log_level(log_level))

# Set Celery configuration
timezone = "UTC"
broker_url = redis_url
broker_connection_retry_on_startup = True
beat_schedule = {
    "check-changelist-every-5-seconds": {
        "task": "check_changelist",
        "schedule": 5.0
    },
    #"check-missing-apps-every-30-minutes": {
    #    "task": "check_missing_apps",
    #    "schedule": 1800.0,
    #},
    "check-incorrect-apps-every-30-minutes": {
        "task": "check_incorrect_apps",
        "schedule": 1800.0,
    },
    "check-deadlocks-every-1-hour": {
        "task": "check_deadlocks",
        "schedule": 3600.0,
    },
}
worker_concurrency = 4

# Dynamically import all tasks files
imports = utils.helper.list_tasks()
