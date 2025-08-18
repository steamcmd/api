import utils.general
import utils.helper
import logging
from dotenv import load_dotenv
from logfmter import Logfmter

# Load values from .env file
_ = load_dotenv()

# Set Redis configuration
redis_url = utils.helper.read_env("REDIS_URL")
redis_host = utils.helper.read_env("REDIS_HOST", "localhost")
redis_port = utils.helper.read_env("REDIS_PORT", "6379")
redis_password = utils.helper.read_env("REDIS_PASSWORD")
redis_database = utils.helper.read_env("REDIS_DATABASE", "0")

# Set RabbitMQ configuration
rabbitmq_host = utils.helper.read_env("RABBITMQ_HOST", "localhost")
rabbitmq_port = utils.helper.read_env("RABBITMQ_PORT", "5672")
rabbitmq_user = utils.helper.read_env("RABBITMQ_USER")
rabbitmq_password = utils.helper.read_env("RABBITMQ_PASSWORD")

# Set general settings
chunk_size = 10
log_level = utils.helper.read_env(
    "LOG_LEVEL", "info", choices=["debug", "info", "warning", "error", "critical"]
)
version = utils.helper.read_env("VERSION", "9.9.9")

# Set logging configuration
formatter = Logfmter(keys=["level"], mapping={"level": "levelname"})
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logging.basicConfig(
    handlers=[handler], level=utils.general.log_level(log_level or "info")
)
logging.getLogger("pika").setLevel(logging.WARNING)

## Tasks configuration
tasks_list = {
    "info": {"interval": 0},  # only manual
    "compare": {"interval": 1800},  # 30 minutes
    "test": {"interval": 10},  # 10 seconds
}
