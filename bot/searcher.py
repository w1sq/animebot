import aiohttp
import asyncio
from copy import copy
import re
from typing import List
from itertools import groupby

def singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


class Title:
    def __init__(self,data:dict) -> None:
        self.id:str = data['id']
        self.imdb_id = data['imdb_id']
        self.title:str = data['title']
        self.orig:str = data['title_orig']
        self.year:int = data['year']
        self.country:List[str] = data['material_data']['countries']
        self.genres:List[str] = data['material_data']['genres']
        self.actors:List[str] = data['material_data']['actors'] 
        self.directors:List[str] = data['material_data']['directors']
        self.poster_url:str = data['material_data']['poster_url']
        self.imdb_rating:str = data['material_data']['imdb_rating']
        self.kinopoisk_rating:float = data['material_data']['kinopoisk_rating']
        self.description:str = data['material_data']['description']

    
    async def load_image(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.poster_url) as pic:
                self.poster_image = await pic.read()

    
    def to_message(self):
        if self.kinopoisk_rating:
            post = f'''
{self.title}
{self.orig}
<u>IMDb: {self.imdb_rating} | КиноПоиск: {self.kinopoisk_rating}</u>


Год: {self.year}
Страна: {', '.join(self.country)}
Жанр: {', '.join(self.genres)}
Актёры: {', '.join(self.actors)}
Режисер: {', '.join(self.directors)}

Описание:
{self.description}
<a href="{self.poster_url}">&#8205</a>
'''
        else:
            post = f'''
{self.title}
{self.orig}
IMDb: {self.imdb_rating}


Год: {self.year}
Страна: {', '.join(self.country)}
Жанр: {', '.join(self.genres)}
Актёры: {', '.join(self.actors)}
Режисер: {', '.join(self.directors)}

Описание:
{self.description}
<a href="{self.poster_url}">&#8205</a>
'''
        return post
    
    def __str__(self):
        return self.to_message()

    def __repr__(self):
        return self.to_message()


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

    async def search(self, phraze, types:str='anime-serial'):  # поиск по названию аниме
        params = copy(self.api_params)
        params.update({'title': phraze, 'types': types})
        results = await self._get(self.search_url, params)

        if results['total'] == 0:
            raise self.NotFoundError('No anime with this name')

        all_titles = results['results']
        titles = self._group(all_titles)

        return titles

    async def _get(self,link,params={}):   # загрузка данных из API
        params['token'] = self.token
        async with aiohttp.ClientSession() as session:
            async with session.get(link,params=params) as resp:
                return await resp.json()



    def _group(self,all_titles):
        titles:List[Title] = []
        for key, group in groupby(all_titles, key=lambda x: x['imdb_id']):
            titles.append(Title(list(group)[0]))
        return titles

 
    async def search_imdb_id(self, link, types:str='anime-serial'):   # поиск по ссылке imdb
        service_id = re.findall(self.imdb_link_exp, link)[0]
        if not service_id:
            raise self.ImdbIncorrectId('Bad imdb link')
        params = copy(self.api_params)
        params.update({'imdb_id': service_id, 'types': types})
        data = await self._get(self.search_url, params)
    
        if data['total'] == 0:
            raise self.NotFoundError('No anime on this link')
        titles = self._group(data['results'])
        return titles
    
    class NotFoundError(Exception):
        pass
    
    class ImdbIncorrectId(Exception):
        pass


    async def search_kinopoisk_id(self, link, types:str='anime-serial'):   # поиск по ссылке kinopoisk
        service_id = re.findall(self.kinopoisk_link_exp, link)[0]
        if not service_id:
            raise self.ImdbIncorrectId('Bad kinopoisk link')
        params = copy(self.api_params)
        params.update({'kinopoisk_id': service_id, 'types': types})
        data = await self._get(self.search_url, params)
        if data['total'] == 0:
            raise self.NotFoundError('No anime on this link')

        titles = self._group(data['results'])

        return titles
    
    class NotFoundError(Exception):
        pass
    
    class ImdbIncorrectId(Exception):
        pass



    async def search_shikimori_id(self, link, types:str='anime-serial'):   # поиск по ссылке imdb
        service_id = re.findall(self.shikimory_link_exp, link)[0]
        if not service_id:
            raise self.ImdbIncorrectId('Bad shikimori link')
        params = copy(self.api_params)
        params.update({'shikimori_id': service_id, 'types': types})
        data = await self._get(self.search_url, params)
        if data['total'] == 0:
            raise self.NotFoundError('No anime on this link')
        titles = self._group(data['results'])
        return titles
    
    class NotFoundError(Exception):
        pass
    
    class ImdbIncorrectId(Exception):
        pass