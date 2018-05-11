from flask import Flask, render_template, jsonify, send_from_directory
import os
from scheduled_cache_updater import get_films, cache

app = Flask(__name__)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


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
