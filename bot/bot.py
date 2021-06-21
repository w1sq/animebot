import asyncio
import logging
from aiogram import Bot, Dispatcher, executor
import aiogram   
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
import sqlite3
from aiogram.dispatcher.filters.state import State, StatesGroup
import re
from searcher import Searcher

searcher =  Searcher()


with open('bot/key.txt','r') as file:
    API_KEY = file.readline()
logging.basicConfig(level=logging.INFO, filename='botlogs.log')
bot = Bot(token=API_KEY)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
con = sqlite3.connect("bot/users.db",check_same_thread=False)
cur = con.cursor()
print('Bot started')

class FormLinkSearchAnime(StatesGroup):
    answer = State()

class FormLinkSearchSeries(StatesGroup):
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
(KeyboardButton('🔎Найти сериал'),KeyboardButton('🔎Найти мультик')).row(KeyboardButton('⭐Избранное'),KeyboardButton('⚙Настройки'))

search_series_keyboard = InlineKeyboardMarkup(resize_keyboard=True).row\
(InlineKeyboardButton(text= '🔎Название',callback_data='name_search_series'),InlineKeyboardButton(text='🔎По ссылке',callback_data='link_search_series'),InlineKeyboardButton(text='🎯Фильтр',callback_data='filter_series'))

search_anime_keyboard = InlineKeyboardMarkup(resize_keyboard=True).row\
(InlineKeyboardButton(text='🔎Название',callback_data='name_search_anime'),InlineKeyboardButton(text='🔎По ссылке',callback_data='link_search_anime'),InlineKeyboardButton(text='🎯Фильтр',callback_data='filter_anime'))

filter_keyboard = InlineKeyboardMarkup(resize_keyboard=True).row\
(InlineKeyboardButton(text='🎭Жанр', callback_data='genre'),InlineKeyboardButton(text='👤Автор', callback_data='author'),InlineKeyboardButton(text='📅Год выпуска', callback_data='date'))

link_processing_series_keyboard = InlineKeyboardMarkup(resize_keyboard=True).row\
(InlineKeyboardButton(text='❌Отмена', callback_data='cancel_processing_series'),InlineKeyboardButton(text=' 🔄Попробовать снова',callback_data='retry_processing_series'))

link_processing_anime_keyboard = InlineKeyboardMarkup(resize_keyboard=True).row\
(InlineKeyboardButton(text='❌Отмена', callback_data='cancel_processing_anime'),InlineKeyboardButton(text=' 🔄Попробовать снова',callback_data='retry_processing_anime'))



@dp.message_handler(commands=['start'])
async def start(message):
    user_id = message.chat.id
    if not cur.execute('''SELECT id FROM user_info
                             WHERE id==?''',(user_id,)).fetchone():
        cur.execute('''INSERT INTO user_info VALUES (?,?,?,?)''',(user_id,'member','',False))
    await message.answer(f'Привет, {message.from_user.username}!\n\nМы самая большая база с Аниме мультфильмами и сериалами.', reply_markup=general_keyboard)


@dp.message_handler(text='🔎Найти сериал')
async def search(message):
    chat_id = message.chat.id
    await message.delete()
    await bot.send_message(chat_id,'*Поиск* \n\nЗдесь вы можете выбрать:\n\n\
    *Поиск по названию* - просто вводим название аниме\n\n\
    *Поиск по ссылке* - нужно прислать ссылку на аниме с кинопоиска или imdb\n\n\
    *Фильтр* - если еще не определились что смотреть, здесь можно отфильтровать тайтлы по некоторым фильтрам.'
    ,reply_markup=search_series_keyboard,parse_mode='Markdown')


@dp.message_handler(text='🔎Найти мультик')
async def search(message):
    chat_id = message.chat.id
    await message.delete()
    await bot.send_message(chat_id,'*Поиск* \n\nЗдесь вы можете выбрать:\n\n\
    *Поиск по названию* - просто вводим название аниме\n\n\
    *Поиск по ссылке* - нужно прислать ссылку на аниме с кинопоиска или imdb\n\n\
    *Фильтр* - если еще не определились что смотреть, здесь можно отфильтровать тайтлы по некоторым фильтрам.'
    ,reply_markup=search_anime_keyboard,parse_mode='Markdown')



@dp.message_handler(text='⭐Избранное')
async def favorite(message):
    chat_id = message.chat.id
    await message.delete()
    await bot.send_message(chat_id=chat_id,text='*Избранное* \n\nЗдесь вы можете найти свои отложенные тайтлы',parse_mode='Markdown')


@dp.message_handler(text='⚙Настройки')
async def settings(message):
    chat_id = message.chat.id
    subscribtion = cur.execute('''
    SELECT subscription from user_info
    WHERE id = ?
    ''',(chat_id,)).fetchone()[0]
    if subscribtion :
        settings_keyboard = generate_inline_keyboard(['❌ Выключить уведомления','unsubscribe'])
    else:
        settings_keyboard = generate_inline_keyboard(['✅ Включить уведомления','subscribe'])
    await message.delete()
    await bot.send_message(chat_id,'*Настройки* \n\nЗдесь вы можете выключить уведомления о новых сериях своих любимых тайтлов',reply_markup=settings_keyboard,parse_mode='Markdown')


async def name_search_series(message):
    await message.answer('Введите название сериал, который хотите посмотреть')

async def name_search_anime(message):
    await message.answer('Введите название аниме, которое хотите посмотреть')


async def link_search_anime(message):
    chat_id = message.chat.id
    await bot.send_message(chat_id,'Укажите ссылку аниме на одной из этих площадок:\n\
                                    www.imdb.com\n\
                                    www.kinopoisk.ru\n\
                                    shikimori.one',parse_mode='Markdown')
    await FormLinkSearchAnime.answer.set()


@dp.message_handler(state=FormLinkSearchAnime.answer)
async def link_processing_anime(message,state):
    if 'imdb.com' in str(message):
        title = await searcher.search_imdb_id(str(message),types='anime')
        for num, i in enumerate(title):
            anime_result_inline_keyboard = InlineKeyboardMarkup(resize_keyboard=True).add(InlineKeyboardButton(text='🍿Смотреть',url=f'http://127.0.0.1:5000/{i.id}')).add(InlineKeyboardButton(text='✅Добавить в мой список аниме',callback_data=f'add_to_favorites_{i.imdb_id}')).add(InlineKeyboardButton(text='🔎Поиск по названию',callback_data='name_search_anime'))
            await message.answer(i,reply_markup=anime_result_inline_keyboard,parse_mode='html')
        await state.finish()
    elif 'kinopoisk.ru' in str(message):
        title = await searcher.search_kinopoisk_id(str(message),types='anime')
        for num, i in enumerate(title):
            anime_result_inline_keyboard = InlineKeyboardMarkup(resize_keyboard=True).add(InlineKeyboardButton(text='🍿Смотреть',url=f'http://127.0.0.1:5000/{i.id}')).add(InlineKeyboardButton(text='✅Добавить в мой список аниме',callback_data=f'add_to_favorites_{i.imdb_id}')).add(InlineKeyboardButton(text='🔎Поиск по названию',callback_data='name_search_anime'))
            await message.answer(i,reply_markup=anime_result_inline_keyboard,parse_mode='html')
        await state.finish()
    elif 'shikimori.one' in str(message):
        title = await searcher.search_shikimori_id(str(message),types='anime')
        for num, i in enumerate(title):
            anime_result_inline_keyboard = InlineKeyboardMarkup(resize_keyboard=True).add(InlineKeyboardButton(text='🍿Смотреть',url=f'http://127.0.0.1:5000/{i.id}')).add(InlineKeyboardButton(text='✅Добавить в мой список аниме',callback_data=f'add_to_favorites_{i.imdb_id}')).add(InlineKeyboardButton(text='🔎Поиск по названию',callback_data='name_search_anime'))
            await message.answer(i,reply_markup=anime_result_inline_keyboard,parse_mode='html')
        await state.finish()
    else:
        await message.answer('Вы ввели неправильную ссылку',reply_markup=link_processing_anime_keyboard)


async def link_search_series(message):
    chat_id = message.chat.id
    await bot.send_message(chat_id,'Укажите ссылку сериала на одной из этих площадок:\n\
                                    www.imdb.com\n\
                                    www.kinopoisk.ru\n\
                                    shikimori.one',parse_mode='Markdown')
    await FormLinkSearchSeries.answer.set()



@dp.message_handler(state=FormLinkSearchSeries.answer)
async def link_processing_anime(message,state):
    if 'imdb.com' in str(message):
        title = await searcher.search_imdb_id(str(message),types='anime-serial')
        for num, i in enumerate(title):
            anime_result_inline_keyboard = InlineKeyboardMarkup(resize_keyboard=True).add(InlineKeyboardButton(text='🍿Смотреть',url=f'http://127.0.0.1:5000/{i.id}')).add(InlineKeyboardButton(text='✅Добавить в мой список аниме',callback_data=f'add_to_favorites_{i.imdb_id}')).add(InlineKeyboardButton(text='🔎Поиск по названию',callback_data='name_search_anime'))
            await bot.send_photo(message.chat.id, i.poster_image,i,reply_markup=anime_result_inline_keyboard)
        await state.finish()
    elif 'kinopoisk.ru' in str(message):
        title = await searcher.search_kinopoisk_id(str(message),types='anime-serial')
        for num, i in enumerate(title):
            anime_result_inline_keyboard = InlineKeyboardMarkup(resize_keyboard=True).add(InlineKeyboardButton(text='🍿Смотреть',url=f'http://127.0.0.1:5000/{i.id}')).add(InlineKeyboardButton(text='✅Добавить в мой список аниме',callback_data=f'add_to_favorites_{i.imdb_id}')).add(InlineKeyboardButton(text='🔎Поиск по названию',callback_data='name_search_anime'))
            await bot.send_photo(message.chat.id, i.poster_image,i,reply_markup=anime_result_inline_keyboard)
        await state.finish()
    elif 'shikimori.one' in str(message):
        title = await searcher.search_shikimori_id(str(message),types='anime-serial')
        for num, i in enumerate(title):
            anime_result_inline_keyboard = InlineKeyboardMarkup(resize_keyboard=True).add(InlineKeyboardButton(text='🍿Смотреть',url=f'http://127.0.0.1:5000/{i.id}')).add(InlineKeyboardButton(text='✅Добавить в мой список аниме',callback_data=f'add_to_favorites_{i.imdb_id}')).add(InlineKeyboardButton(text='🔎Поиск по названию',callback_data='name_search_anime'))
            await bot.send_photo(message.chat.id, i.poster_image,i,reply_markup=anime_result_inline_keyboard)
        await state.finish()
    else:
        await message.answer('Вы ввели неправильную ссылку',reply_markup=link_processing_anime_keyboard)


async def filtr_series(message):
    chat_id = message.chat.id
    await bot.send_message(chat_id,'Укажите параметры фильтра сеариалов',reply_markup=filter_keyboard,parse_mode='Markdown')


async def filtr_anime(message):
    chat_id = message.chat.id
    await bot.send_message(chat_id,'Укажите параметры фильтра аниме',reply_markup=filter_keyboard,parse_mode='Markdown')


async def cancel_processing_series(message):
    pass


async def cancel_processing_anime(message):
    pass


async def add_to_favorites(message,id):
    pass



async def subscribe(message):
    cur.execute('''
    UPDATE user_info
    SET subscription = ?
    WHERE id = ?
    ''',(True,message.chat.id,))
    await settings(message)

async def unsubscribe(message):
    cur.execute('''
    UPDATE user_info
    SET subscription = ?
    WHERE id = ?
    ''',(False,message.chat.id,))
    await settings(message)


@dp.callback_query_handler(lambda call: True)
async def ans(call):
    message = call.message
    if call.data == 'name_search_series':
        await call.message.delete()
        await name_search_series(message)
    elif call.data == 'name_search_anime':
        await call.message.delete()
        await name_search_series(message)
    elif call.data == 'link_search_series':
        await call.message.delete()
        await link_search_series(message)
    elif call.data == 'link_search_anime':
        await call.message.delete()
        await link_search_anime(message)
    elif call.data == 'filter_series':
        await filtr_series(message)
    elif call.data == 'filter_anime':
        await filtr_series(message)
    elif call.data == 'cancel_processing_series':
        await cancel_processing_series(message)
    elif call.data == 'cancel_processing_anime':
        await cancel_processing_anime(message)
    elif call.data == 'unsubscribe':
        await call.answer('Вы успешно отключили уведомления')
        await unsubscribe(message)
    elif call.data == 'subscribe':
        await call.answer('Вы успешно включили уведомления')
        await subscribe(message)
    elif call.data == 'cancel_processing':
        pass
    elif 'add_to_favorites' in call.data :
        id = re.findall(re.compile(r'tt\d+'), call.data)[0]
        await add_to_favorites(message,id)

async def main():
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())