from celery import Celery
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the Celery application
app = Celery()
app.config_from_object("config")
app.autodiscover_tasks(["main.tasks"])
