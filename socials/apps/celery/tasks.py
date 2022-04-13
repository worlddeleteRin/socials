from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger
import logging
import requests
import time

logger = get_task_logger(__name__)
logger.setLevel(logging.DEBUG)
app = Celery()

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        3,
        # crontab(1),
        make_bot_tasks.s()
    )

@app.task()
def make_bot_tasks():
    logger.info("sleeping for 10 seconds...")
    logger.info("something")
