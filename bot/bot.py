# coding=utf8
import asyncio
import logging
from aiogram import Bot, Dispatcher, executor,types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InputTextMessageContent, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultPhoto
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import re
from aiogram.dispatcher.filters import Text
from aiogram.types.inline_query_result import InlineQueryResultArticle
from db_data import db_session
from db_data.__all_models import Users, Anime
from searcher import Searcher


searcher =  Searcher()


with open('bot/key.txt','r') as file:
    API_KEY = file.readline()
logging.basicConfig(level=logging.INFO, filename='botlogs.log')
bot = Bot(token=API_KEY)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db_session.global_init()
print('Bot started')


class FormLinkSearchAnime(StatesGroup):
    answer = State()
 
class FormLinkSearchSeries(StatesGroup):
    answer = State()


class FormNameSearchAnime(StatesGroup):
    answer = State()

class FormNameSearchSeries(StatesGroup):
    answer = State()



def generate_keyboard (*answer):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    temp_buttons = []
    for i in answer:
        temp_buttons.append(KeyboardButton(text=i))
    keyboard.add(*temp_buttons)
    return keyboard

def generate_inline_keyboard (*answer):
    keyboard = InlineKeyboardMarkup()
    temp_buttons = []
    for i in answer:
        temp_buttons.append(InlineKeyboardButton(text=str(i[0]), callback_data=i[1]))
    keyboard.add(*temp_buttons)
    return keyboard

general_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row\
(KeyboardButton('🔎 Найти сериал'),KeyboardButton('🔎 Найти мультик')).row(KeyboardButton('🆕 Новинки'),KeyboardButton('⭐ Избранное')).row(KeyboardButton('⚙ Настройки'))

search_series_keyboard = InlineKeyboardMarkup(resize_keyboard=True).row\
(InlineKeyboardButton(text= '🔎 Название',switch_inline_query_current_chat="#serial "),).row(InlineKeyboardButton(text='🔎 Кинопоиск',switch_inline_query_current_chat="#kp_serial "),InlineKeyboardButton(text='🔎 IMDB',switch_inline_query_current_chat="#imd_serial "),InlineKeyboardButton(text='🔎 Shikimori',switch_inline_query_current_chat="#shik_serial ")).row(InlineKeyboardButton(text='🔎 По ссылке',switch_inline_query_current_chat="#link_series "),InlineKeyboardButton(text='🎯 Фильтр',callback_data='filter_series'))

search_anime_keyboard = InlineKeyboardMarkup(resize_keyboard=True).row\
(InlineKeyboardButton(text='🔎 Название',switch_inline_query_current_chat="#anime ")).row(InlineKeyboardButton(text='🔎 Кинопоиск',switch_inline_query_current_chat="#kp_anime "),InlineKeyboardButton(text='🔎 IMDB',switch_inline_query_current_chat="#imdb_anime "),InlineKeyboardButton(text='🔎 Shikimori',switch_inline_query_current_chat="#shk_anime ")).row(InlineKeyboardButton(text='🔎 По ссылке',switch_inline_query_current_chat="#link_anime "),InlineKeyboardButton(text='🎯 Фильтр',callback_data='filter_anime'))

filter_anime_keyboard = InlineKeyboardMarkup(resize_keyboard=True).row\
(InlineKeyboardButton(text='🎭 Жанр', callback_data='genre'),InlineKeyboardButton(text='📅 Год выпуска', callback_data='date')).row(InlineKeyboardButton(text='Очистить фильтр',callback_data='clear_filters'))

filter_series_keyboard = InlineKeyboardMarkup(resize_keyboard=True).row\
(InlineKeyboardButton(text='🎭 Жанр', callback_data='genre'),InlineKeyboardButton(text='📅 Год выпуска', callback_data='date')).row(InlineKeyboardButton(text='Очистить фильтр',callback_data='clear_filters'))


new_keyboard = InlineKeyboardMarkup(resize_keyboard=True).row(InlineKeyboardButton(text='Показать новинки',switch_inline_query_current_chat="#new "))


@dp.message_handler(commands=['start'])
async def start(message):
    user_id = message.chat.id
    db_sess = db_session.create_session()
    db_sess.close()
    user = db_sess.query(Users).get(user_id)
    if not user:
        user = Users(
            id = user_id
        )
        db_sess.add(user)
        db_sess.commit()
        db_sess.close()
    await message.answer(f'Привет, {message.from_user.username}!\n\nМы самая большая база с Аниме мультфильмами и сериалами.', reply_markup=general_keyboard)


@dp.message_handler(state='*', commands='❌Отмена')
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='❌Отмена', ignore_case=True), state='*')
async def cancel_handler(state: FSMContext):
    current_state = await state.get_state()

    logging.info('Cancelling state %r', current_state)
    await state.finish()


async def send_titles(titles,query,cache_time=1,text='✅ Добавить в мой список аниме',callback_data='add_to_favorites'):
    results = []
    db_sess = db_session.create_session()
    for num,i in enumerate(titles):
        try:
            results.append(
                InlineQueryResultArticle(
                    id=num+1,
                    title=i.title,
                    thumb_url= i.poster_link,
                    description=f'{i.imdb_rating} {i.kinopoisk_rating}',
                    reply_markup=InlineKeyboardMarkup(resize_keyboard=True).add(InlineKeyboardButton(text='🍿 Смотреть',url=f'http://127.0.0.1:5000/id/{i.kodik_id}')).add(InlineKeyboardButton(text=text,callback_data=f'{callback_data}#{i.kodik_id}')).add(InlineKeyboardButton(text='🔎 Поиск по названию',switch_inline_query_current_chat="#all ")),
                    input_message_content=InputTextMessageContent(
                        message_text=i.to_message(),parse_mode='html'
                    
                    )
                )
            )
        except Exception:
            results.append(
                InlineQueryResultArticle(
                    id=num+1,
                    title=i.title,
                    thumb_url= i.poster_link,
                    description=f'{i.imdb_rating} {i.kinopoisk_rating}',
                    reply_markup=InlineKeyboardMarkup(resize_keyboard=True).add(InlineKeyboardButton(text='🍿 Смотреть',url=f'http://127.0.0.1:5000/id/{i.kodik_id}')).add(InlineKeyboardButton(text=text,callback_data=f'{callback_data}#{i.kodik_id}')).add(InlineKeyboardButton(text='🔎 Поиск по названию',switch_inline_query_current_chat="#all ")),
                    input_message_content=InputTextMessageContent(
                        message_text=i.to_message(),parse_mode='html'
                    
                    )
                )
            )
    if query and not results:
        results.append(
            InlineQueryResultArticle(
                id=999,
                title='Ничего не нашлось',
                thumb_url= 'https://котовчанин.рф/content/uploads/2017/10/stranica-ne-naydena.jpeg',
                input_message_content=InputTextMessageContent(
                    message_text=f'Ничего не нашлось',
                ),
            )
        )
    await query.answer(
        results=results,
        cache_time=cache_time,
        switch_pm_text="Перейти в бот",
        switch_pm_parameter="start"
    )


@dp.inline_handler(text="#fav", state="*")
async def inline_handler(query: types.InlineQuery):
    db_sess = db_session.create_session()
    user_id = query['from']['id']
    favorites = db_sess.query(Users).get(user_id).favorites
    await send_titles(titles = favorites,query=query,cache_time=1,text='❌ Удалить из моего списка аниме',callback_data='remove_from_favorites')


@dp.inline_handler(text="", state="*")
@dp.inline_handler(text="#new", state="*")
async def inline_handler(query: types.InlineQuery):
    titles = await searcher.news()
    await send_titles(titles,query,cache_time=1)


@dp.inline_handler(lambda query: query.query.startswith('#all'), state="*")
async def inline_handler(query: types.InlineQuery):
    titles = await searcher.search(str(query.query).strip().lower()[4:])
    await send_titles(titles,query)


@dp.inline_handler(lambda query: query.query.startswith('#shk_serial'), state="*")
async def inline_handler(query: types.InlineQuery):
    titles = await searcher.search(str(query.query).strip().lower()[11:],types='anime-serial',sort='shikimori_rating')
    await send_titles(titles,query)


@dp.inline_handler(lambda query: query.query.startswith('#anime'), state="*")
async def inline_handler(query: types.InlineQuery):
    titles = await searcher.search(str(query.query).strip().lower()[6:],types='anime')
    await send_titles(titles,query)


@dp.inline_handler(lambda query: query.query.startswith('#kp_anime'), state="*")
async def inline_handler(query: types.InlineQuery):
    titles = await searcher.search(str(query.query).strip().lower()[9:],types='anime',sort='kinopoisk_rating')
    await send_titles(titles,query)


@dp.inline_handler(lambda query: query.query.startswith('#imdb_anime'), state="*")
async def inline_handler(query: types.InlineQuery):
    titles = await searcher.search(str(query.query).strip().lower()[11:],types='anime',sort='imdb_rating')
    await send_titles(titles,query)


@dp.inline_handler(lambda query: query.query.startswith('#shk_anime'), state="*")
async def inline_handler(query: types.InlineQuery):
    titles = await searcher.search(str(query.query).strip().lower()[10:],types='anime',sort='shikimori_rating')
    await send_titles(titles,query)

@dp.inline_handler(lambda query: query.query.startswith('#link_anime'), state="*")
async def inline_handler(query: types.InlineQuery):
    link = str(query.query).strip().lower()[11:]
    if 'imdb.com' in link:
        titles = await searcher.search_imdb_id(link,types='anime')
    elif 'kinopoisk.ru' in link:
        titles = await searcher.search_kinopoisk_id(link,types='anime')
    elif 'shikimori.one' in link:
        titles = await searcher.search_shikimori_id(link,types='anime')
    await send_titles(titles,query)


@dp.inline_handler(lambda query: query.query.startswith('#serial'), state="*")
async def inline_handler(query: types.InlineQuery):
    titles = await searcher.search(str(query.query).strip().lower()[7:],types='anime-serial')
    await send_titles(titles,query)


@dp.inline_handler(lambda query: query.query.startswith('#kinp_serial'), state="*")
async def inline_handler(query: types.InlineQuery):
    titles = await searcher.search(str(query.query).strip().lower()[12:],types='anime-serial',sort='kinopoisk_rating')
    await send_titles(titles,query)


@dp.inline_handler(lambda query: query.query.startswith('#imd_serial'), state="*")
async def inline_handler(query: types.InlineQuery):
    titles = await searcher.search(str(query.query).strip().lower()[11:],types='anime-serial',sort='imdb_rating')
    await send_titles(titles,query)


@dp.inline_handler(lambda query: query.query.startswith('#shik_serial'), state="*")
async def inline_handler(query: types.InlineQuery):
    titles = await searcher.search(str(query.query).strip().lower()[12:],types='anime-serial',sort='shikimori_rating')
    await send_titles(titles,query)

@dp.inline_handler(lambda query: query.query.startswith('#link_series'), state="*")
async def inline_handler(query: types.InlineQuery):
    link = str(query.query).strip().lower()[12:]
    if 'imdb.com' in link:
        titles = await searcher.search_imdb_id(link,types='anime-serial')
    elif 'kinopoisk.ru' in link:
        titles = await searcher.search_kinopoisk_id(link,types='anime-serial')
    elif 'shikimori.one' in link:
        titles = await searcher.search_shikimori_id(link,types='anime-serial')
    await send_titles(titles,query)


@dp.message_handler(text='🔎 Найти сериал')
async def search(message):
    await message.delete()
    await message.answer('''Поиск
    
    Здесь вы можете выбрать:

    Поиск по названию - просто вводим название сериала

    Кинопоиск, Imdb, Shikimori - поиск сериала,но с сортировкой
    по рейтинку определенной площадки

    Поиск по ссылке - нужно прислать ссылку на сериал с
    <a href="www.kinopoisk.ru">Кинопоиска</a>, <a href="www.imdb.com">Imdb</a> или <a href="shikimori.one">Shikimori</a>

    Фильтр - если еще не определились что смотреть, 
    здесь можно отфильтровать сериалы по некоторым фильтрам.'''
    ,reply_markup=search_series_keyboard,parse_mode='html',disable_web_page_preview=True)


@dp.message_handler(text='🔎 Найти мультик')
async def search(message):
    await message.delete()
    await message.answer('''Поиск
    
    Здесь вы можете выбрать:

    Поиск по названию - просто вводим название аниме

    Кинопоиск, Imdb, Shikimori - поиск аниме,но с сортировкой
    по рейтинку определенной площадки

    Поиск по ссылке - нужно прислать ссылку на аниме с
    <a href="www.kinopoisk.ru">Кинопоиска</a>, <a href="www.imdb.com">Imdb</a> или <a href="shikimori.one">Shikimori</a>

    Фильтр - если еще не определились что смотреть, 
    здесь можно отфильтровать аниме по некоторым фильтрам.'''
    ,reply_markup=search_anime_keyboard,parse_mode='html',disable_web_page_preview=True)



@dp.message_handler(text='⭐ Избранное')
async def favorite(message):
    chat_id = message.chat.id
    await message.delete()
    fav_keyboard = InlineKeyboardMarkup(resize_keyboard=True).add(InlineKeyboardButton(text= 'Перейти к любимому',switch_inline_query_current_chat="#fav "))
    await bot.send_message(chat_id=chat_id,text='*Избранное* \n\nЗдесь вы можете найти свои отложенные тайтлы',parse_mode='Markdown',reply_markup=fav_keyboard)


@dp.message_handler(text='🆕 Новинки')
async def search(message):
    chat_id = message.chat.id
    await message.delete()
    await bot.send_message(chat_id,'*Новинки* \n\nПоказать последние тайты?'
    ,reply_markup=new_keyboard,parse_mode='Markdown')


@dp.message_handler(text='⚙ Настройки')
async def settings(message):
    user_id = message.chat.id
    db_sess = db_session.create_session()
    subscribtion = db_sess.query(Users).get(user_id).notifications
    db_sess.close()
    if subscribtion :
        settings_keyboard = generate_inline_keyboard(['❌ Выключить уведомления','unsubscribe'])
    else:
        settings_keyboard = generate_inline_keyboard(['✅ Включить уведомления','subscribe'])
    await bot.send_message(user_id,'*Настройки* \n\nЗдесь вы можете выключить уведомления о новых сериях своих любимых тайтлов',reply_markup=settings_keyboard,parse_mode='Markdown')


async def filtr_series(message):
    chat_id = message.chat.id
    await bot.send_message(chat_id,'Укажите параметры фильтра сериалов',reply_markup=filter_series_keyboard,parse_mode='Markdown')


async def filtr_anime(message):
    chat_id = message.chat.id
    await bot.send_message(chat_id,'Укажите параметры фильтра аниме',reply_markup=filter_anime_keyboard,parse_mode='Markdown')

async def add_to_favorites(user_id,id):
    db_sess = db_session.create_session()
    anime = db_sess.query(Anime).filter(Anime.kodik_id == id).first()
    user= db_sess.query(Users).get(user_id)
    user.favorites.append(anime)
    db_sess.commit()
    db_sess.close()


async def remove_from_favorites(user_id,id):
    db_sess = db_session.create_session()
    anime = db_sess.query(Anime).filter(Anime.kodik_id == id).first()
    user= db_sess.query(Users).get(user_id)
    user.favorites.remove(anime)
    db_sess.commit()
    db_sess.close()


async def subscribe(message):
    user_id = message.chat.id
    db_sess = db_session.create_session()
    user = db_sess.query(Users).get(user_id)
    user.notifications=True
    db_sess.commit()
    db_sess.close()

async def unsubscribe(message):
    user_id = message.chat.id
    db_sess = db_session.create_session()
    user = db_sess.query(Users).get(user_id)
    user.notifications=False
    db_sess.commit()
    db_sess.close()


@dp.callback_query_handler(lambda call: True)
async def ans(call):
    message = call.message
    if call.data == 'filter_series':
        await filtr_series(message)
    elif call.data == 'filter_anime':
        await filtr_series(message)
    elif call.data == 'unsubscribe':
        await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup= generate_inline_keyboard(['✅ Включить уведомления','subscribe']))
        await call.answer('Вы успешно отключили уведомления')
        await unsubscribe(message)
    elif call.data == 'subscribe':
        await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=generate_inline_keyboard(['❌ Выключить уведомления','unsubscribe']))
        await call.answer('Вы успешно включили уведомления')
        await subscribe(message)
    elif call.data == 'cancel':
        await call.answer('Отменено')
        await cancel_handler()
    elif 'remove_from_favorites' in call.data:
        await call.answer('Удалено из избранных')
        user_id = call.from_user.id
        id = call.data.split('#')[1]
        await remove_from_favorites(user_id,id)
    elif 'add_to_favorites' in call.data :
        await call.answer('Добавлено в избранное')
        user_id = call.from_user.id
        id = call.data.split('#')[1]
        await add_to_favorites(user_id,id)
        
        
async def main():
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())