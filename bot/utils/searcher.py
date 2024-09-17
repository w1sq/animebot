import aiohttp
import asyncio
from copy import copy
import re
from typing import List
from itertools import groupby
from db_data import db_session
from db_data.__all_models import Users, Anime


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


def add_to_db(title, db_sess):
    anime = db_sess.query(Anime).filter(Anime.kodik_id == str(title.kodik_id)).first()
    if not anime:
        anime = Anime(
            kodik_id=title.kodik_id,
            title=title.title,
            title_orig=title.orig,
            iframe_link=title.iframe_link,
            status="finished",
            poster_link=title.poster_link,
            imdb_rating=title.imdb_rating,
            kinopoisk_rating=title.kinopoisk_rating,
            year=title.year,
            genres=title.genres,
            actors=title.actors,
            directors=title.directors,
            description=title.description,
        )
        db_sess.add(anime)
        db_sess.commit()
        db_sess.close()


class AnimeTitle:
    def __init__(self, data: dict) -> None:
        self.kodik_id: str = data.get("id", "")
        self.shikimori_id = data.get("shikimori_id", "")
        self.title: str = data.get("title", "")
        self.orig: str = data.get("title_orig", "")
        self.iframe_link: str = data.get("link", "")
        if data.get("material_data", "") != "":
            self.poster_link: str = data["material_data"].get("poster_url", "")
            self.status: str = data["material_data"].get("all_status", "ongoing")
            self.year: str = f"Год: {data.get('year','')}\n"
            self.genres: str = (
                f"Жанр: {', '.join(data['material_data'].get('genres',''))}\n"
            )
            self.actors: str = (
                f"Актёры: {', '.join(data['material_data'].get('actors',''))}\n"
            )
            self.directors: str = (
                f"Режисер: {', '.join(data['material_data'].get('directors',''))}"
            )
            self.imdb_rating: str = (
                f"IMDb: {data['material_data'].get('imdb_rating','')}"
            )
            self.kinopoisk_rating: str = (
                f"| КиноПоиск: {data['material_data'].get('kinopoisk_rating','')}"
            )
            self.description: str = f"""Описание:\n{data['material_data'].get('description','')}
    <a href="{data['material_data'].get('poster_url','')}">&#8205</a>
----------------------------------------------------------------------
    @animepointbot - Самая большая база с аниме мультфильмами и сериалами."""
        else:
            self.poster_link: str = ""
            self.status: str = "ongoing"
            self.year: str = f"Год: {data.get('year','')}\n"
            self.genres: str = "Жанр: \n"
            self.actors: str = "Актёры: \n"
            self.directors: str = "Режисер: "
            self.imdb_rating: str = f"IMDb: "
            self.kinopoisk_rating: str = f"| КиноПоиск: "
            self.description: str = f"""Описание:\n
----------------------------------------------------------------------
    @animepointbot - Самая большая база с аниме мультфильмами и сериалами."""

    def to_message(self):
        return f"""
{self.title}
{self.orig}
<u>{self.imdb_rating} {self.kinopoisk_rating} </u>

{self.year}{self.genres}{self.actors}{self.directors}

{self.description}
"""

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.title


def get_data(data, name):
    res = data.get(name, "")
    if not res:
        return ""
    return res


class FilmTitle:
    def __init__(self, data: dict) -> None:
        self.kodik_id: str = get_data(data, "id")
        self.title: str = get_data(data, "name")
        self.orig: str = get_data(data, "name_eng")
        self.iframe_link: str = get_data(data, "iframe_url")
        self.poster_link: str = get_data(data, "poster")
        self.quality: str = f"Качество: {get_data(data,'quality')}"
        self.actors: str = f"Актёры: {', '.join(data.get('actors',[]))}\n"
        self.directors: str = f"Режисер: {', '.join(data.get('director',[]))}"
        self.genres: str = f"Жанр: {', '.join(data.get('genre',{}).values())}\n"
        self.year: str = f"Год: {get_data(data,'year')}\n"
        self.imdb_rating: str = f"IMDb: {get_data(data,'imdb')}"
        self.kinopoisk_rating: str = f"| КиноПоиск: {get_data(data,'kinopoisk')}"
        self.description: str = f"""Описание:\n{get_data(data,'description')}
<a href="{self.poster_link}">&#8205</a>
----------------------------------------------------------------------
@animepointbot - Самая большая база с аниме мультфильмами и сериалами."""

    def to_message(self):
        return f"""
{self.title}
{self.orig}
{self.quality}
<u>{self.imdb_rating} {self.kinopoisk_rating} </u>

{self.year}{self.genres}{self.actors}{self.directors}

{self.description}
"""

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.title


@singleton
class Films_Searcher:
    def __init__(self):
        self.list_url = "https://api1647279397.bhcesh.me/list"
        self.search_url = "https://api1647279397.bhcesh.me/franchise/details"
        self.token = "404c284ad24e337a0334c93a837edcec"
        self.api_params = {
            "limit": 20,
        }
        self.imdb_link_exp = re.compile(r"tt\d+")
        self.kinopoisk_link_exp = re.compile(r"\/(\d+)\/")
        self.world_art_link_exp = re.compile(r"\d+")

    async def _group(self, all_titles, session, phraze=""):
        titles: List[FilmTitle] = []
        db_sess = db_session.create_session()
        try:
            for key, group in groupby(all_titles, key=lambda x: x["id"]):
                group = list(group)[0]
                if phraze:
                    if all(
                        [
                            title_lower in group["title"].lower()
                            for title_lower in phraze.lower().split()
                        ]
                    ):
                        group = await self._get_info(group["id"], session)
                        title = FilmTitle(group)
                        add_to_db(title, db_sess)
                        titles.append(title)
                else:
                    group = await self._get_info(group["id"], session)
                    title = FilmTitle(group)
                    add_to_db(title, db_sess)
                    titles.append(title)
        except Exception:
            try:
                titles = []
                for key, group in groupby(all_titles, key=lambda x: x["imdb_id"]):
                    group = list(group)[0]
                    if phraze:
                        if all(
                            [
                                title_lower in group["title"].lower()
                                for title_lower in phraze.lower().split()
                            ]
                        ):
                            group = await self._get_info(group["id"], session)
                            title = FilmTitle(group)
                            add_to_db(title, db_sess)
                            titles.append(title)
                    else:
                        group = await self._get_info(group["id"], session)
                        title = FilmTitle(group)
                        add_to_db(title, db_sess)
                        titles.append(title)
            except Exception:
                try:
                    titles = []
                    for key, group in groupby(all_titles, key=lambda x: x["name"]):
                        group = list(group)[0]
                        if phraze:
                            if all(
                                [
                                    title_lower in group["title"].lower()
                                    for title_lower in phraze.lower().split()
                                ]
                            ):
                                group = await self._get_info(group["id"], session)
                                title = FilmTitle(group)
                                add_to_db(title, db_sess)
                                titles.append(title)
                        else:
                            group = await self._get_info(group["id"], session)
                            title = FilmTitle(group)
                            add_to_db(title, db_sess)
                            titles.append(title)
                except Exception:
                    pass
        return titles

    async def _get(
        self, link, params={}, token=False, phraze=""
    ):  # загрузка данных из API
        if token:
            params["token"] = self.token
        print(params)
        async with aiohttp.ClientSession() as session:
            async with session.get(link, params=params) as resp:
                results = await resp.json()
                titles = await self._group(results["results"], session, phraze)
        results["results"] = titles
        return results

    async def _get_info(self, id, session):
        params = {"id": id, "token": self.token}
        async with session.get(self.search_url, params=params) as resp:
            return await resp.json()

    async def load_next_page(self, url):
        url = (
            "https://api1647279397.bhcesh.me/list?"
            + url.replace("_", "&")
            + "&token=404c284ad24e337a0334c93a837edcec"
        )
        results = await self._get(url)
        if results["next_page"]:
            return results["results"], results["next_page"]
        else:
            return results["results"], ""

    async def news(self):
        params = copy(self.api_params)
        params.update({"types": "films", "sort": "-year"})
        titles = await self._get(self.list_url, params, token=True)
        if titles["next_page"]:
            return titles["results"], titles["next_page"]
        else:
            return titles["results"], ""

    async def search_imdb_id(self, link, types: str):  # поиск по ссылке imdb
        service_id = re.findall(self.imdb_link_exp, link)[0]
        if not service_id:
            return [], ""
        params = copy(self.api_params)
        params.update({"imdb_id": service_id.replace("tt", ""), "type": types})
        results = await self._get(self.list_url, params, token=True)
        return results["results"]

    async def search_kinopoisk_id(self, link, types: str):  # поиск по ссылке kinopoisk
        service_id = re.findall(self.kinopoisk_link_exp, link)[0]
        if not service_id:
            return [], ""
        params = copy(self.api_params)
        params.update({"kinopoisk_id": service_id, "type": types})
        results = await self._get(self.list_url, params, token=True)
        return results["results"]

    async def search_world_art_id(self, link, types: str):  # поиск по ссылке kinopoisk
        service_id = re.findall(self.world_art_link_exp, link)[0]
        if not service_id:
            return [], ""
        params = copy(self.api_params)
        params.update({"world_art_id": service_id, "type": types})
        results = await self._get(self.list_url, params, token=True)
        return results["results"]

    async def search(self, phraze, types: str):  # поиск по названию аниме
        params = copy(self.api_params)
        params.update({"type": types, "limit": 30})
        print(phraze)
        if str(phraze).strip() != "":
            params.update({"name": phraze.strip()})
            titles = await self._get(self.list_url, params, token=True)
        else:
            titles = await self._get(self.list_url, params, token=True)
        if titles["next_page"]:
            return titles["results"], titles["next_page"]
        else:
            return titles["results"], ""


@singleton
class Anime_Searcher:
    def __init__(self):
        self.token = "50fa8bac3f0ce0a3d9b6ff1f2cd4adbf"
        self.search_url = "https://kodikapi.com/search"
        self.list_url = "https://kodikapi.com/list"
        self.api_params = {
            "with_material_data": "true",
        }
        self.imdb_link_exp = re.compile(r"tt\d+")
        self.kinopoisk_link_exp = re.compile(r"\/(\d+)\/")
        self.shikimory_link_exp = re.compile(r"\/(\d+)\-")

    async def load_next_page(self, num):
        url = f"https://kodikapi.com/list?token=7f129085d2f372833fcc5e2116e4d0a4&page={num}"
        results = await self._get(url)
        titles = self._group(results["results"])
        try:
            return titles, results["next_page"]
        except Exception:
            return titles, ""

    async def load_anime(self, types, sort=""):
        params = copy(self.api_params)
        params.update({"types": types, "sort": sort, "order": "desc", "limit": 50})
        results = await self._get(self.list_url, params)
        titles = self._group(results["results"])
        if results["next_page"]:
            return titles, results["next_page"]
        else:
            return titles, ""

    async def search(self, phraze, types: str):  # поиск по названию аниме
        params = copy(self.api_params)
        if types:
            params.update({"types": types})
        params.update({"limit": 50})
        if str(phraze).strip() != "":
            params.update({"title": phraze})
            results = await self._get(self.search_url, params)
            if results["total"] == 0:
                return [], ""
            titles = self._group_by_name(results["results"], phraze)
        else:
            results = await self._get(self.list_url, params)
            if results["total"] == 0:
                return [], ""
            titles = self._group(results["results"])
        try:
            return titles, results["next_page"]
        except Exception:
            return titles, ""

    async def _get(self, link, params={}):  # загрузка данных из API
        params["token"] = self.token
        async with aiohttp.ClientSession() as session:
            async with session.get(link, params=params) as resp:
                return await resp.json()

    def _group_by_name(self, all_titles, title):
        titles: List[AnimeTitle] = []
        db_sess = db_session.create_session()
        try:
            for key, group in groupby(all_titles, key=lambda x: x["shikimori_id"]):
                group = list(group)[0]
                if all(
                    [
                        title_lower in group["title"].lower()
                        for title_lower in title.lower().split()
                    ]
                ):
                    group = AnimeTitle(group)
                    titles.append(group)
        except Exception:
            try:
                titles = []
                for key, group in groupby(all_titles, key=lambda x: x["imdb_id"]):
                    group = list(group)[0]
                    if all(
                        [
                            title_lower in group["title"].lower()
                            for title_lower in title.lower().split()
                        ]
                    ):
                        group = AnimeTitle(group)
                        titles.append(group)
            except Exception:
                titles = []
                for key, group in groupby(all_titles, key=lambda x: x["title"]):
                    group = list(group)[0]
                    if all(
                        [
                            title_lower in group["title"].lower()
                            for title_lower in title.lower().split()
                        ]
                    ):
                        group = AnimeTitle(group)
                        titles.append(group)

        for title in titles:
            anime = (
                db_sess.query(Anime).filter(Anime.kodik_id == title.kodik_id).first()
            )
            if not anime:
                anime = Anime(
                    kodik_id=title.kodik_id,
                    title=title.title,
                    title_orig=title.orig,
                    iframe_link=title.iframe_link,
                    status=title.status,
                    poster_link=title.poster_link,
                    imdb_rating=title.imdb_rating,
                    kinopoisk_rating=title.kinopoisk_rating,
                    year=title.year,
                    genres=title.genres,
                    actors=title.actors,
                    directors=title.directors,
                    description=title.description,
                )
                db_sess.add(anime)
                db_sess.commit()
                db_sess.close()
        return titles

    def _group(self, all_titles):
        titles: List[AnimeTitle] = []
        db_sess = db_session.create_session()
        try:
            for key, group in groupby(all_titles, key=lambda x: x["shikimori_id"]):
                group = AnimeTitle(list(group)[0])
                titles.append(group)
        except Exception:
            try:
                titles = []
                for key, group in groupby(all_titles, key=lambda x: x["imdb_id"]):
                    group = AnimeTitle(list(group)[0])
                    titles.append(group)
            except Exception:
                titles = []
                for key, group in groupby(all_titles, key=lambda x: x["title"]):
                    group = AnimeTitle(list(group)[0])
                    titles.append(group)

        for title in titles:
            anime = (
                db_sess.query(Anime).filter(Anime.kodik_id == title.kodik_id).first()
            )
            if not anime:
                anime = Anime(
                    kodik_id=title.kodik_id,
                    title=title.title,
                    title_orig=title.orig,
                    iframe_link=title.iframe_link,
                    status=title.status,
                    poster_link=title.poster_link,
                    imdb_rating=title.imdb_rating,
                    kinopoisk_rating=title.kinopoisk_rating,
                    year=title.year,
                    genres=title.genres,
                    actors=title.actors,
                    directors=title.directors,
                    description=title.description,
                )
                db_sess.add(anime)
                db_sess.commit()
                db_sess.close()
        return titles

    async def news(self):
        params = copy(self.api_params)
        params.update({"types": "anime,anime-serial", "sort": "year"})
        results = await self._get(self.list_url, params)
        titles = self._group(results["results"])
        with open("test.json", "w") as f:
            f.write(str(results))
        if results["next_page"]:
            return titles, results["next_page"]
        else:
            return titles, ""

    async def search_imdb_id(self, link, types: str):  # поиск по ссылке imdb
        service_id = re.findall(self.imdb_link_exp, link)[0]
        if not service_id:
            return [], ""
        params = copy(self.api_params)
        params.update({"imdb_id": service_id, "types": types})
        results = await self._get(self.search_url, params)

        if results["total"] == 0:
            return [], ""
        titles = self._group(results["results"])
        return titles

    async def search_kinopoisk_id(self, link, types: str):  # поиск по ссылке kinopoisk
        service_id = re.findall(self.kinopoisk_link_exp, link)[0]
        if not service_id:
            return [], ""
        params = copy(self.api_params)
        params.update({"kinopoisk_id": service_id, "types": types})
        results = await self._get(self.search_url, params)
        if results["total"] == 0:
            return [], ""

        titles = self._group(results["results"])

        return titles

    async def search_shikimori_id(self, link, types: str):  # поиск по ссылке imdb
        service_id = re.findall(self.shikimory_link_exp, link)[0]
        if not service_id:
            return [], ""
        params = copy(self.api_params)
        params.update({"shikimori_id": service_id, "types": types})
        results = await self._get(self.search_url, params)
        if results["total"] == 0:
            return [], ""
        titles = self._group(results["results"])
        return titles
