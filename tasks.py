import threading
from queue import Queue
import requests
import pyprind

### FIXME: No GLOBALS !!
done = 0


def download_file(url):
    cc = url.split('/')[-1]
    extension = cc.split('-')[-1]
    local_filename = "-".join(cc.split('-')[:-1])
    r = requests.get(url, stream=True)
    file_name = '{0}.{1}'.format(local_filename, extension)

    with open(file_name, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()


class PremkaTaks(threading.Thread):
    def __init__(self, q, tasks):
        self.queue = q
        self.tasks = tasks
        threading.Thread.__init__(self)
        self.start()

    def run(self):
        while not self.queue.empty():
            url = self.queue.get()
            download_file(url)
            global done
            done += 1
        self.tasks.task_done()


class PremkaTasksPool:
    def __init__(self, num, q):
        self.tasks = Queue(num)
        for _ in range(num):
            self.tasks.put(PremkaTaks(q, self.tasks))

    def wait(self):
        self.tasks.join()


def f_print(max):
    global done
    tmp = done
    bar = pyprind.ProgBar(max)
    while not done >= max:
        if tmp != done:
            bar.update()
            tmp = done


def download_files(links, threads):
    q = Queue()
    for link in links:
        q.put(link)
    max = q.qsize()
    pool = PremkaTasksPool(threads, q)
    t = threading.Thread(target=f_print, args=(max,))
    t.start()
    pool.wait()
    t.join()
