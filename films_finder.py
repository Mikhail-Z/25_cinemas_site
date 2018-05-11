from bs4 import BeautifulSoup
import requests
import re


def fetch_page(url):
    return requests.get(url).text


def parse_film_raw_info(raw_film_info):
    raw_main_film_info = raw_film_info.find("a", "card__link")
    name = raw_main_film_info.find("h3", "card__title").text.strip()
    try:
        description = raw_main_film_info.find("p", "card__verdict").text.strip()
    except AttributeError:
        description = ""
    image_link = raw_main_film_info.find("img", "card__image")["src"]
    try:
        score = float(raw_film_info.find("div", "rating__selector-value").text.strip())
    except AttributeError:
        score = 5.0

    cinemas_num_str = raw_film_info.find("div", {"itemprop": "location"}).find(
        "meta", {"itemprop": "name"})["content"]
    cinemas_num = int(re.search(r"\d+", cinemas_num_str).group())

    genre = raw_film_info.find("a", "card__badge").text.strip()
    afisha_url = "https://www.afisha.ru"
    film_on_afisha_url = "{}{}".format(afisha_url, raw_main_film_info["href"])
    return {
        "name": name,
        "description": description,
        "image": image_link,
        "score": score,
        "cinemas_num": cinemas_num,
        "genre": genre,
        "url_on_afisha": film_on_afisha_url
    }


def parse_afisha_list(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    raw_info_about_films = soup.find_all("div", "card cards-grid__item")
    films_info = []
    cinemas_num_when_film_is_arthouse = 30

    for i, raw_film_info in enumerate(raw_info_about_films):
        film_info = parse_film_raw_info(raw_film_info)
        if film_info["cinemas_num"] > cinemas_num_when_film_is_arthouse:
            films_info.append(film_info)
    return films_info


def rating_formula(film):
    return film["cinemas_num"]+film["score"]**3


def get_best_films(top_num=10):
    url_for_films_list = "https://www.afisha.ru/msk/schedule_cinema/"
    afisha_page = fetch_page(url_for_films_list)
    films_list = parse_afisha_list(afisha_page)
    films_list.sort(key=lambda film: rating_formula(film), reverse=True)
    return films_list[:min(len(films_list), top_num)]
