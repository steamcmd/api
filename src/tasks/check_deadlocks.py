from main import app, logger
from celery_singleton import clear_locks


@app.task(name="check_deadlocks", bind=True)
def check_deadlocks_task(self):
    """
    If no running tasks, purge all singleton locks
    in Redis to avoid for ever deadlocks.
    """

    workers = app.control.inspect()
    workers = workers.active()

    total_tasks = []
    for worker in workers:
        active_tasks = workers[worker]
        for task in active_tasks:
            if task["id"] != self.request.id:
                total_tasks.append(task)

    clear_locks(app)

    logger.info("Cleared locks. No tasks were running.")
