from werkzeug.contrib.cache import FileSystemCache
from time import sleep
from films_finder import get_best_films
import threading
import tempfile

ONE_HOUR = 60 * 60


cache = FileSystemCache(tempfile.gettempdir(), default_timeout=ONE_HOUR)


def update_cache():
    top_number = 10
    films = get_best_films(top_number)
    lock = threading.Lock()
    lock.acquire()
    cache.set('/', films)
    lock.release()
    return films


def update_cache_periodically():
    while True:
        update_cache()
        update_period = int(ONE_HOUR/2)
        sleep(update_period)


def get_films():
    films = cache.get('/')
    if films is None:
        films = update_cache()
    return films
