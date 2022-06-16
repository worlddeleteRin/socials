from threading import Thread

from run_tasks_vk import process_tasks as process_vk_tasks
from run_tasks_ok import process_tasks as process_ok_tasks
from run_tasks_yt import process_tasks as process_yt_tasks
from socials.logging import lgd,lgw,lge

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
    vk_tasks = VkTasksThread()
    ok_tasks = OkTasksThread()
    yt_tasks = YtTasksThread()

    vk_tasks.start()
    ok_tasks.start()
