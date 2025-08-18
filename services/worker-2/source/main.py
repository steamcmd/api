# type: ignore[import]

"""
Worker Service.
"""

# Import modules
import utils.helper
import utils.config

imports = utils.helper.list_tasks()
from celery import Celery
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialise Celery application
app = Celery()
app.config_from_object("utils.config")
app.autodiscover_tasks(["main.tasks"])
