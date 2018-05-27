from bs4 import BeautifulSoup
import requests
import re
import threading
from math import ceil


def fetch_page(url):
    return requests.get(url).text


def get_film_description(raw_film_info):
    try:
        description = raw_film_info.find("p", "card__verdict").text.strip()
    except AttributeError:
        description = ""
    return description


def get_film_score(raw_film_info):
    default_score = 5.0
    try:
        score = float(raw_film_info.find("div", "rating__selector-value").text.strip())
    except AttributeError:
        score = default_score
    return score


def get_cinemas_num_with_film(raw_film_info):
    cinemas_num_str = raw_film_info.find("div", {"itemprop": "location"}).find(
        "meta", {"itemprop": "name"})["content"]
    cinemas_num = int(re.search(r"\d+", cinemas_num_str).group())
    return cinemas_num


def get_film_page_on_afisha(raw_film_info):
    afisha_url = "https://www.afisha.ru"
    film_on_afisha_url = "{}{}".format(afisha_url, raw_film_info["href"])
    return film_on_afisha_url


def parse_films_raw_info(raw_films_info, film_info, fst_idx, last_idx):
    for raw_film_info in raw_films_info[fst_idx: last_idx]:
        raw_film_main_info = raw_film_info.find("a", "card__link")
        title = raw_film_main_info.find("h3", "card__title").text.strip()
        description = get_film_description(raw_film_main_info)
        image_link = raw_film_main_info.find("img", "card__image")["src"]
        score = get_film_score(raw_film_info)
        cinemas_num = get_cinemas_num_with_film(raw_film_info)
        genre = raw_film_info.find("a", "card__badge").text.strip()
        film_on_afisha_url = get_film_page_on_afisha(raw_film_main_info)
        cinemas_num_when_film_is_arthouse = 30
        if cinemas_num > cinemas_num_when_film_is_arthouse:
            film_info.append({
                "title": title,
                "description": description,
                "image": image_link,
                "score": score,
                "cinemas_num": cinemas_num,
                "genre": genre,
                "url_on_afisha": film_on_afisha_url
            })


def parse_afisha_list(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    raw_info_about_films = soup.find_all("div", "card cards-grid__item")

    threads_num = 8
    films_num = len(raw_info_about_films)
    films_per_thread = int(ceil(films_num / threads_num))
    threads = []
    films_info = []

    for fst_film_idx_for_thread in range(0, films_num, films_per_thread):
        last_film_idx_for_thread = min(fst_film_idx_for_thread+films_per_thread, films_num)
        thread = threading.Thread(
            target=parse_films_raw_info,
            args=(
                raw_info_about_films, films_info,
                fst_film_idx_for_thread, last_film_idx_for_thread,
            )
        )
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    return films_info


def rating_formula(film):
    return film["cinemas_num"]+film["score"]**3


def get_best_films(top_num=10):
    url_for_films_list = "https://www.afisha.ru/msk/schedule_cinema/"
    afisha_page = fetch_page(url_for_films_list)
    films_list = parse_afisha_list(afisha_page)
    films_list.sort(key=lambda film: rating_formula(film), reverse=True)
    return films_list[:min(len(films_list), top_num)]
