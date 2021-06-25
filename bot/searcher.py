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


class Title:
    def __init__(self,data:dict) -> None:
        self.kodik_id:str = data.get('id','')
        self.shikimori_id = data.get('shikimori_id','')
        self.title:str = data.get('title','')
        self.orig:str = data.get('title_orig','')
        self.iframe_link:str = data.get('link','')
        if data.get('material_data','')!= '':
            self.poster_link:str = data['material_data'].get('poster_url','')
            self.status:str = data['material_data'].get('all_status','ongoing')
            self.year:str = f"Год: {data.get('year','')}\n"
            self.genres:str = f"Жанр: {', '.join(data['material_data'].get('genres',''))}\n"
            self.actors:str = f"Актёры: {', '.join(data['material_data'].get('actors',''))}\n" 
            self.directors:str = f"Режисер: {', '.join(data['material_data'].get('directors',''))}"
            self.imdb_rating:str = f"IMDb: {data['material_data'].get('imdb_rating','')}"
            self.kinopoisk_rating:str = f"| КиноПоиск: {data['material_data'].get('kinopoisk_rating','')}"
            self.description:str = f'''Описание:\n{data['material_data'].get('description','')}
    <a href="{data['material_data'].get('poster_url','')}">&#8205</a>
----------------------------------------------------------------------
    @animepointbot - Самая большая база с аниме мультфильмами и сериалами.'''
        else:
            self.poster_link:str = ''
            self.status:str = 'ongoing'
            self.year:str = f"Год: {data.get('year','')}\n"
            self.genres:str = "Жанр: \n"
            self.actors:str = "Актёры: \n" 
            self.directors:str = "Режисер: "
            self.imdb_rating:str = f"IMDb: "
            self.kinopoisk_rating:str = f"| КиноПоиск: "
            self.description:str = f'''Описание:\n
----------------------------------------------------------------------
    @animepointbot - Самая большая база с аниме мультфильмами и сериалами.'''
    



    def to_message(self):
        return f'''
{self.title}
{self.orig}
<u>{self.imdb_rating} {self.kinopoisk_rating} </u>

{self.year}{self.genres}{self.actors}{self.directors}

{self.description}
'''
    
    def __str__(self):
        return self.title

    def __repr__(self):
        return self.title

@singleton
class Searcher():
    def __init__(self):
        self.token = '50fa8bac3f0ce0a3d9b6ff1f2cd4adbf'
        self.search_url = 'https://kodikapi.com/search'
        self.list_url = 'https://kodikapi.com/list'
        self.api_params = {'with_material_data' : 'true',}
        self.imdb_link_exp = re.compile(r'tt\d+')
        self.kinopoisk_link_exp = re.compile(r'\/(\d+)\/')
        self.shikimory_link_exp = re.compile(r'\/(\d+)\-')

    async def search(self, phraze, types:str='anime-serial, anime',sort=''):  # поиск по названию аниме
        params = copy(self.api_params)
        params.update({'types': types})
        if str(phraze).strip() != '':
            if not sort:
                params.update({'title': phraze})
                results = await self._get(self.search_url, params)
            else:
                params.update({'title': phraze,'sort':sort})
                results = await self._get(self.list_url, params)
                print(results)
        else:
            results = await self._get(self.list_url, params)
        if results['total'] == 0:
            raise self.NotFoundError('No anime with this name')

        all_titles = results['results']
        titles = self._group_by_name(all_titles,phraze)

        return titles

    async def _get(self,link,params={}):   # загрузка данных из API
        params['token'] = self.token
        async with aiohttp.ClientSession() as session:
            async with session.get(link,params=params) as resp:
                return await resp.json()



    def _group_by_name(self,all_titles,title):
        titles:List[Title] = []
        db_sess = db_session.create_session()
        try:
            for key, group in groupby(all_titles, key=lambda x: x['shikimori_id']):
                group = list(group)[0]            
                if all([title_lower in group['title'].lower() for title_lower in title.lower().split()]):
                    group = Title(group)
                    titles.append(group)
        except Exception:
            try:
                titles=[]
                for key, group in groupby(all_titles, key=lambda x: x['imdb_id']):
                    group = list(group)[0]            
                    if all([title_lower in group['title'].lower() for title_lower in title.lower().split()]):
                        group = Title(group)
                        titles.append(group)
            except Exception:
                titles=[]
                for key, group in groupby(all_titles, key=lambda x: x['title']):
                    group = list(group)[0]            
                    if all([title_lower in group['title'].lower() for title_lower in title.lower().split()]):
                        group = Title(group)
                        titles.append(group)
        for title in titles:
            anime = db_sess.query(Anime).filter(Anime.kodik_id == title.kodik_id).first()
            if not anime:
                anime = Anime(
                    kodik_id = title.kodik_id,
                    title = title.title,
                    title_orig = title.orig,
                    iframe_link = title.iframe_link,
                    status = title.status,
                    poster_link = title.poster_link,
                    imdb_rating = title.imdb_rating,
                    kinopoisk_rating = title.kinopoisk_rating,
                    year = title.year,
                    genres = title.genres,
                    actors = title.actors,
                    directors = title.directors,
                    description = title.description
                )
                db_sess.add(anime)
                db_sess.commit()
                db_sess.close()
        return titles

    
    
    def _group(self,all_titles):
        titles:List[Title] = []
        db_sess = db_session.create_session()
        try:
            for key, group in groupby(all_titles, key=lambda x: x['shikimori_id']):
                group = Title(list(group)[0])
                titles.append(group)
        except Exception:
            try:
                for key, group in groupby(all_titles, key=lambda x: x['imdb_id']):
                    group = Title(list(group)[0])
                    titles.append(group)
            except Exception:
                for key, group in groupby(all_titles, key=lambda x: x['title']):
                    group = Title(list(group)[0])
                    titles.append(group)
        for title in titles:
            anime = db_sess.query(Anime).filter(Anime.kodik_id == title.kodik_id).first()
            if not anime:
                anime = Anime(
                    kodik_id = title.kodik_id,
                    title = title.title,
                    title_orig = title.orig,
                    iframe_link = title.iframe_link,
                    status = title.status,
                    poster_link = title.poster_link,
                    imdb_rating = title.imdb_rating,
                    kinopoisk_rating = title.kinopoisk_rating,
                    year = title.year,
                    genres = title.genres,
                    actors = title.actors,
                    directors = title.directors,
                    description = title.description
                )
                db_sess.add(anime)
                db_sess.commit()
                db_sess.close()    
        return titles



    async def news(self):
        params = copy(self.api_params)
        params.update({'types':'anime,anime-serial','sort':'year'})
        results = await self._get(self.list_url, params)
        titles = self._group(results['results'])
        return titles

 
    async def search_imdb_id(self, link, types:str='anime-serial'):   # поиск по ссылке imdb
        service_id = re.findall(self.imdb_link_exp, link)[0]
        if not service_id:
            raise self.Bad_link('Bad link')
        params = copy(self.api_params)
        params.update({'imdb_id': service_id, 'types': types})
        results = await self._get(self.search_url, params)
    
        if results['total'] == 0:
            raise self.NotFoundError('No anime on this link')
        titles = self._group(results['results'])
        return titles
    
    class NotFoundError(Exception):
        pass
    
    class Bad_link(Exception):
        pass


    async def search_kinopoisk_id(self, link, types:str='anime-serial'):   # поиск по ссылке kinopoisk
        service_id = re.findall(self.kinopoisk_link_exp, link)[0]
        if not service_id:
            raise self.Bad_link('Bad link')
        params = copy(self.api_params)
        params.update({'kinopoisk_id': service_id, 'types': types})
        results = await self._get(self.search_url, params)
        if results['total'] == 0:
            raise self.NotFoundError('No anime on this link')

        titles = self._group(results['results'])

        return titles


    async def search_shikimori_id(self, link, types:str='anime-serial'):   # поиск по ссылке imdb
        service_id = re.findall(self.shikimory_link_exp, link)[0]
        if not service_id:
            raise self.Bad_link('Bad link')
        params = copy(self.api_params)
        params.update({'shikimori_id': service_id, 'types': types})
        results = await self._get(self.search_url, params)
        if results['total'] == 0:
            raise self.NotFoundError('No anime on this link')
        titles = self._group(results['results'])
        return titles


    async def filter_search(self,filters:dict, types:str='anime-serial'):
        params = copy(self.api_params)
        params.update({'types': types})
        for anime_filter in filters:
            params.update({anime_filter['param']: anime_filter['value']})
        results = await self._get(self.search_url, params)

        if results['total'] == 0:
            raise self.NotFoundError('No anime with these filters')

        all_titles = results['results']
        titles = self._group(all_titles)

        return titles