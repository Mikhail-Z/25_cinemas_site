from bs4 import BeautifulSoup
import requests
import re
from math import ceil, floor
import threading


def fetch_page(url):
    return requests.get(url).text


def parse_afisha_list(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    raw_info = soup.find_all("div", "object s-votes-hover-area collapsed")
    raw_film_names_and_urls = [elem.find("h3", "usetags") for elem in raw_info]

    film_names = [elem.text for elem in raw_film_names_and_urls]
    cinemas_num = [len(elem.find_all("td", "b-td-item")) for elem in raw_info]
    films_url_on_afisha = [elem.find("a")["href"] for elem in raw_film_names_and_urls]
    cinemas_num_when_film_is_arthouse = 30
    return [
        {
            "name": film_name,
            "cinemas_num": cinemas_num,
            "url_on_afisha": film_url_on_afisha
        }
        for film_name, cinemas_num, film_url_on_afisha in zip(
            film_names, cinemas_num, films_url_on_afisha
        )
        if cinemas_num > cinemas_num_when_film_is_arthouse
    ]


def fetch_film_page(film_url):
    return requests.get(film_url).text


def replace_non_break_space(text):
    return text.replace("\xa0", " ")


def parse_film_photos_page(soup):
    photo_url = soup.find("img", id="ctl00_CenterPlaceHolder_ucPhotoPageContent_imgBigPhoto")["src"]
    return photo_url


def get_photo_from_film(url):
    page_with_photos = fetch_page(url)
    soup = BeautifulSoup(page_with_photos, "html.parser")
    film_photo_url = parse_film_photos_page(soup)
    return film_photo_url


def get_film_rating_and_votes(soup):
    raw_film_rating_and_votes = soup.find("div", "b-rating-big s-display-rating")
    film_rating_string = raw_film_rating_and_votes.find("p", class_="stars pngfix")["title"]
    if film_rating_string == "":
        film_rating = 0.0
    else:
        film_rating = float(
            re.search(r"(\d(,\d)?)", film_rating_string).group(1).replace(',', '.'))
    film_votes = raw_film_rating_and_votes.find(
        "p", class_="details s-update-clickcount"
    ).span.span.text
    return film_rating, film_votes


def parse_film_page(soup):
    raw_genre_info = soup.find("div", class_="b-tags")
    film_genres = [raw_genre.text for raw_genre in raw_genre_info.find_all("a")]
    film_rating, film_votes = get_film_rating_and_votes(soup)
    photos_from_film_page_url = "https://afisha.ru{}".format(soup.find("a", id="ctl00_CenterPlaceHolder_ucTab_rpTabs_ctl04_hlItem")["href"])
    film_photo_url = get_photo_from_film(photos_from_film_page_url)
    max_genre_count = 2
    info_from_afisha = {
        "genre": ", ".join(film_genres[:min(len(film_genres), max_genre_count)]),
        "rating": film_rating,
        "votes": int(film_votes.strip()),
        "photo_url": film_photo_url
    }
    return info_from_afisha


def get_film_info(film_url):
    film_page = fetch_film_page(film_url)
    soup = BeautifulSoup(film_page, "html.parser")
    additional_info = parse_film_page(soup)
    return additional_info


def rating_formula(film):
    return film["cinemas_num"]*(4*film["votes"] + film["rating"]**4)


def get_stars_count(rating):
    decimal_number = rating*10 % 10
    has_half_star = True if 3 < decimal_number <= 8 else False
    full_stars_count = ceil(rating) if decimal_number > 8 else floor(rating)
    return full_stars_count, has_half_star


def get_films_info(films):
    for film in films:
        film.update(get_film_info(film["url_on_afisha"]))
        film["stars"] = get_stars_count(film["rating"])


def get_best_films(top_num=10):
    url_for_films_list = "https://www.afisha.ru/msk/schedule_cinema/"
    afisha_page = fetch_page(url_for_films_list)
    films_list = parse_afisha_list(afisha_page)
    films_num = len(films_list)
    threads_num = 8
    films_per_thread = int(ceil(films_num / threads_num))
    threads = []
    for i in range(0, films_num, films_per_thread):
        thread = threading.Thread(
            target=get_films_info,
            args=(films_list[i:min(films_num, i+films_per_thread)],)
        )
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    films_list.sort(key=lambda film: rating_formula(film), reverse=True)
    return films_list[:min(len(films_list), top_num)]
