from werkzeug.contrib.cache import FileSystemCache
from films_finder import get_best_films

ONE_HOUR = 60 * 60

CACHE_DIR = "."

cache = FileSystemCache(CACHE_DIR, default_timeout=ONE_HOUR)


def update_cache():
    top_number = 10
    films = get_best_films(top_number)
    cache.set('/', films)


def get_films():
    films = cache.get('/')
    if films is None:
        update_cache()
        films = cache.get('/')
    return films
