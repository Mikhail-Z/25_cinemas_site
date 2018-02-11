from apscheduler.schedulers.background import BackgroundScheduler
from films_finder import get_best_films
import atexit
from werkzeug.contrib.cache import FileSystemCache

scheduler = BackgroundScheduler()
cache = FileSystemCache('cache', default_timeout=60)


def update_cache():
    top_number = 10
    films = get_best_films(top_number)
    cache.set('/', films)
    return films

# 55 минут выбрано, так как время обновления кэша должно быть меньше времени
# действия кэша (1 час), иначе обновления кэша (долго) произойдет во время
# обращения к сервису пользователя

scheduler.add_job(update_cache, 'interval', seconds=30, replace_existing=True)

scheduler.start()

atexit.register(lambda: scheduler.shutdown())