from threading import Thread
import argparse
from typing import List

from run_tasks_vk import process_tasks as process_vk_tasks
from run_tasks_ok import process_tasks as process_ok_tasks
from run_tasks_yt import process_tasks as process_yt_tasks
from socials.apps.bots.models import PlatformEnum
from socials.logging import lgd,lgw,lge

parser = argparse.ArgumentParser(description='Some arguments parser')
parser.add_argument(
    '--run-platforms', 
    '-p',
    nargs='+',
    default=[],
    help='Specify regular tasks platforms to run'
)
parser.add_argument(
    '--run-platforms-selenium', 
    '-ps',
    nargs='+',
    default=[],
    help='Specify selenium tasks platforms to run'
)
parser.add_argument(
    '--selenium-yt-threads', 
    default=3,
    type=int,
    help='Specify threads number for youtube selenium tasks'
)

class VkTasksThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        lgd('** Starting vk tasks thread **')
        while True:
            process_vk_tasks(include_selenium_tasks=False)

class OkTasksThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        lgd('** Starting ok tasks thread **')
        while True:
            process_ok_tasks(include_selenium_tasks=False)

class OkSeleniumTasksThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        lgd('** Starting youtube SELENIUM tasks thread **')
        while True:
            process_ok_tasks(
                include_selenium_tasks=True,
                process_tasks_per_cycle=10
            )

class YtTasksThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        lgd('** Starting youtube tasks thread **')
        while True:
            process_yt_tasks(include_selenium_tasks=False)

class YtSeleniumTasksThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        lgd('** Starting youtube SELENIUM tasks thread **')
        while True:
            process_yt_tasks(
                include_selenium_tasks=True,
                process_tasks_per_cycle=1
            )

if __name__ == '__main__':
    args = parser.parse_args()
    lgd(f'args are {args}')
    run_platforms = args.run_platforms
    run_platforms_selenium = args.run_platforms_selenium
    selenium_yt_threads = args.selenium_yt_threads

    platforms: list[Thread] = []
    if run_platforms and len(run_platforms) > 0:
        if PlatformEnum.vk in run_platforms:
            vk_tasks = VkTasksThread()
            platforms.append(vk_tasks)
        if PlatformEnum.ok in run_platforms:
            ok_tasks = OkTasksThread()
            platforms.append(ok_tasks)
        if PlatformEnum.yt in run_platforms:
            yt_tasks = YtTasksThread()
            platforms.append(yt_tasks)

    selenium_platforms: list[Thread] = []
    if run_platforms_selenium and len(run_platforms_selenium) > 0:
        if PlatformEnum.yt in run_platforms_selenium:
            for i in range(0,selenium_yt_threads):
                yt_tasks = YtSeleniumTasksThread()
                selenium_platforms.append(yt_tasks)
        if PlatformEnum.ok in run_platforms_selenium:
            for i in range(0,1):
                ok_tasks = OkSeleniumTasksThread()
                selenium_platforms.append(ok_tasks)
    
    lgd(f'Attempting to start {len(platforms)} platforms tasks & {len(selenium_platforms)} selenium platforms tasks')
    # start platforms
    for p in platforms:
        p.start()
    # start selenium platforms
    for p in selenium_platforms:
        p.start()
