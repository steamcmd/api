"""
Job Service and background worker.
"""

# import modules
from celery import Celery
import logging

# set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# initialise Celery application
app = Celery()
app.config_from_object("config")
app.autodiscover_tasks(["job.tasks"])
