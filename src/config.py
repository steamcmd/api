import utils.helper
import logging

# fmt: off

# Set variables based on environment
redis_host = utils.helper.read_env("REDIS_HOST", "localhost")
redis_port = utils.helper.read_env("REDIS_PORT", "6379")
redis_url = "redis://" + redis_host + ":" + redis_port + "/0"

storage_type = utils.helper.read_env("STORAGE_TYPE", "local", choices=[ "local", "object" ])
storage_directory = utils.helper.read_env("STORAGE_DIRECTORY", "data/", dependency={ "STORAGE_TYPE": "local" })
storage_object_endpoint = utils.helper.read_env("STORAGE_OBJECT_ENDPOINT", dependency={ "STORAGE_TYPE": "object" })
storage_object_access_key = utils.helper.read_env("STORAGE_OBJECT_ACCESS_KEY", dependency={ "STORAGE_TYPE": "object" })
storage_object_secret_key = utils.helper.read_env("STORAGE_OBJECT_SECRET_KEY", dependency={ "STORAGE_TYPE": "object" })
storage_object_bucket = utils.helper.read_env("STORAGE_OBJECT_BUCKET", dependency={ "STORAGE_TYPE": "object" })
storage_object_secure = utils.helper.read_env("STORAGE_OBJECT_SECURE", True)
storage_object_region = utils.helper.read_env("STORAGE_OBJECT_REGION", False)

# Set general settings
chunk_size = 10

# logging configuration
formatter = Logfmter(keys=["level"], mapping={"level": "levelname"})
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logging.basicConfig(handlers=[handler])
if "LOG_LEVEL" in os.environ:
    log_level(os.environ["LOG_LEVEL"])

# Set Celery configuration
timezone = "UTC"
broker_url = redis_url
broker_connection_retry_on_startup = True
beat_schedule = {
    "check-changelist-every-5-seconds": {
        "task": "check_changelist",
        "schedule": 5.0
    },
    "check-missing-apps-every-30-minutes": {
        "task": "check_missing_apps",
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
