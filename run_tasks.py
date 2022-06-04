from threading import Thread

from run_tasks_vk import process_tasks as process_vk_tasks
from run_tasks_ok import process_tasks as process_ok_tasks
from socials.logging import lgd,lgw,lge

class VkTasksThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        lgd('** Starting vk tasks thread **')
        while True:
            process_vk_tasks()

class OkTasksThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        lgd('** Starting ok tasks thread **')
        while True:
            process_ok_tasks()

if __name__ == '__main__':
    vk_tasks = VkTasksThread()
    ok_tasks = OkTasksThread()

    vk_tasks.start()
    ok_tasks.start()
