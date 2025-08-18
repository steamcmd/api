"""
Manual trigger task.
"""

# Import modules
import utils.config
import utils.rabbitmq
import logging
import sys

# Get task name from command line argument
if len(sys.argv) != 2:
    print("Usage: python task.py <task_name>")
    sys.exit(1)
task = sys.argv[1]

# Check if task is defined
if not utils.config.tasks_list[task]:
    print("Incorrect task defined")
    sys.exit(1)

# Start specified task
utils.rabbitmq.message(task)

logging.info("Manually scheduled task", extra={"task": task})
