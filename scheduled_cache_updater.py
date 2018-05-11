from werkzeug.contrib.cache import FileSystemCache
from films_finder import get_best_films
import tempfile

ONE_DAY = 60 * 60 * 24


cache = FileSystemCache(tempfile.gettempdir(), default_timeout=ONE_DAY)


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
