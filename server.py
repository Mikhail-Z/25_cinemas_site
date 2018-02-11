from flask import Flask, render_template, jsonify, send_from_directory
import os
from films_finder import get_best_films
from scheduled_cache_updater import cache


ONE_HOUR = 60 * 60

app = Flask(__name__)


def update_cache():
    top_number = 10
    films = get_best_films(top_number)
    cache.set('/', films)
    return films


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


def get_films():
    films = cache.get('/')
    print(films)
    if films is None:
        films = update_cache()
    return films


@app.route('/')
def films_list():
    films = get_films()
    return render_template('films_list.html', films=films)


@app.route('/api')
def api():
    films = get_films()
    return jsonify(films)


@app.route('/api/documentation')
def api_documentation():
    return render_template('api_documentation.html')


if __name__ == "__main__":
    app.run()
