# coding=utf8

import os
import logging
from dotenv import load_dotenv

import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from db_data import db_session
from db_data.__all_models import Users
from utils.searcher import Anime_Searcher, Films_Searcher
from utils.generators import (
    generate_inline_keyboard,
    generate_inline_link_keyboard,
)
from utils.Keyboards import (
    all_anime_keyb,
    search_anime_keyboard,
    search_anime_series_keyboard,
    search_series_keyboard,
    search_mult_keyboard,
    search_movie_keyboard,
    new_keyboard_anime,
    new_keyboard_films,
    all_kino_keyb,
    search_multseries_keyboard,
)
from utils.Forms import FormMessage
from utils.moderators import (
    send_titles,
    add_to_favorites,
    remove_from_favorites,
    remove_films,
    show_films,
)

admins = [631874013, 418396366, 621553386]
anime_searcher = Anime_Searcher()
films_searcher = Films_Searcher()

load_dotenv(dotenv_path=".env")
API_KEY = os.getenv("API_KEY")
logging.basicConfig(level=logging.INFO, filename="botlogs.log")
bot = Bot(token=API_KEY)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db_session.global_init(os.getenv("CONN_STR"))
print("Bot started")


@dp.message_handler(commands=["reboot"])
async def reboot(message):
    if message.chat.id in admins:
        await message.answer("Server is rebooting")
        await message.delete()
        os.system("reboot")


@dp.message_handler(commands=["help"])
async def help(message):
    await message.answer(
        "О нашем Боте и часто задаваемые вопросы https://telegra.ph/Otvety-na-chasto-zadavaemye-voprosy-03-18-3"
    )


@dp.message_handler(commands=["start"])
async def start(message):
    user_id = message.chat.id
    db_sess = db_session.create_session()
    user = db_sess.query(Users).get(user_id)
    if not user:
        user = Users(id=user_id)
        db_sess.add(user)
        db_sess.commit()
        db_sess.close()
    await message.answer(
        f"Привет, {message.from_user.username}!\n\nМы самая большая база с Аниме мультфильмами и сериалами.",
        reply_markup=all_anime_keyb,
    )


@dp.message_handler(state="*", commands="❌Отмена")
@dp.message_handler(state="*", commands="cancel")
@dp.message_handler(Text(equals="❌Отмена", ignore_case=True), state="*")
async def cancel_handler(state: FSMContext):
    current_state = await state.get_state()
    logging.info("Cancelling state %r", current_state)
    await state.finish()


@dp.inline_handler(text="#fav", state="*")
async def inline_handler(query: types.InlineQuery):
    db_sess = db_session.create_session()
    user_id = query["from"]["id"]
    favorites = db_sess.query(Users).get(user_id).favorites
    await send_titles(
        titles=favorites,
        query=query,
        cache_time=1,
        text="❌ Удалить из понравившегося",
        callback_data="remove_from_favorites",
    )


@dp.inline_handler(text="", state="*")
@dp.inline_handler(text="#newanime", state="*")
async def inline_handler(query: types.InlineQuery):
    if query.offset:
        titles, next = await anime_searcher.load_next_page(query.offset)
    else:
        titles, next = await anime_searcher.news()
    if next:
        next = next.split("=")[2]
    await send_titles(titles, query, cache_time=1, next_offset=next)


@dp.inline_handler(text="#newfilms", state="*")
async def inline_handler(query: types.InlineQuery):
    if query.offset:
        titles, next = await films_searcher.load_next_page(query.offset)
    else:
        titles, next = await films_searcher.news()
    if next:
        next = (
            next.split("?")[1]
            .replace("&token=404c284ad24e337a0334c93a837edcec", "")
            .replace("&", "_")
        )
    await send_titles(titles, query, cache_time=15, next_offset=next)


@dp.inline_handler(lambda query: query.query.startswith("#all"), state="*")
async def inline_handler(query: types.InlineQuery):
    if query.offset:
        titles, next = await anime_searcher.load_next_page(query.offset)
    else:
        titles, next = await anime_searcher.search(
            phraze=str(query.query).strip().lower()[4:], types=""
        )
    if next:
        next = next.split("=")[2]
    await send_titles(titles, query, cache_time=5, next_offset=next)


@dp.inline_handler(lambda query: query.query.startswith("#anime"), state="*")
async def inline_handler(query: types.InlineQuery):
    if query.offset:
        titles, next = await anime_searcher.load_next_page(query.offset)
    else:
        titles, next = await anime_searcher.search(
            phraze=str(query.query).strip().lower()[6:], types="anime"
        )
    if next:
        next = next.split("=")[2]
    await send_titles(titles, query, cache_time=1, next_offset=next)


@dp.inline_handler(lambda query: query.query.startswith("#kp_anime"), state="*")
async def inline_handler(query: types.InlineQuery):
    if query.offset:
        titles, next = await anime_searcher.load_next_page(query.offset)
    else:
        titles, next = await anime_searcher.load_anime(
            types="anime", sort="kinopoisk_rating"
        )
    if next:
        next = next.split("=")[2]
    await send_titles(titles, query, cache_time=1, next_offset=next)


@dp.inline_handler(lambda query: query.query.startswith("#imdb_anime"), state="*")
async def inline_handler(query: types.InlineQuery):
    if query.offset:
        titles, next = await anime_searcher.load_next_page(query.offset)
    else:
        titles, next = await anime_searcher.load_anime(
            types="anime", sort="imdb_rating"
        )
    if next:
        next = next.split("=")[2]
    await send_titles(titles, query, cache_time=1, next_offset=next)


@dp.inline_handler(lambda query: query.query.startswith("#shk_anime"), state="*")
async def inline_handler(query: types.InlineQuery):
    if query.offset:
        titles, next = await anime_searcher.load_next_page(query.offset)
    else:
        titles, next = await anime_searcher.load_anime(
            types="anime", sort="shikimori_rating"
        )
    if next:
        next = next.split("=")[2]
    await send_titles(titles, query, cache_time=1, next_offset=next)


@dp.inline_handler(lambda query: query.query.startswith("#link_anime"), state="*")
async def inline_handler(query: types.InlineQuery):
    link = str(query.query).strip().lower()[11:]
    if "imdb.com" in link:
        titles = await anime_searcher.search_imdb_id(link, types="anime")
    elif "kinopoisk.ru" in link:
        titles = await anime_searcher.search_kinopoisk_id(link, types="anime")
    elif "shikimori.one" in link:
        titles = await anime_searcher.search_shikimori_id(link, types="anime")
    else:
        titles = []
    await send_titles(titles, query)


@dp.inline_handler(lambda query: query.query.startswith("#animserial"), state="*")
async def inline_handler(query: types.InlineQuery):
    if query.offset != "":
        titles, next = await anime_searcher.load_next_page(query.offset)
    else:
        titles, next = await anime_searcher.search(
            phraze=str(query.query).strip().lower()[11:], types="anime-serial"
        )
    if next:
        next = next.split("=")[2]
    await send_titles(titles, query, cache_time=1, next_offset=next)


@dp.inline_handler(lambda query: query.query.startswith("#kinp_animserial"), state="*")
async def inline_handler(query: types.InlineQuery):
    if query.offset:
        titles, next = await anime_searcher.load_next_page(query.offset)
    else:
        titles, next = await anime_searcher.load_anime(
            types="anime-serial", sort="kinopoisk_rating"
        )
    if next:
        next = next.split("=")[2]
    await send_titles(titles, query, cache_time=1, next_offset=next)


@dp.inline_handler(lambda query: query.query.startswith("#imd_animserial"), state="*")
async def inline_handler(query: types.InlineQuery):
    if query.offset:
        titles, next = await anime_searcher.load_next_page(query.offset)
    else:
        titles, next = await anime_searcher.load_anime(
            types="anime-serial", sort="imdb_rating"
        )
    if next:
        next = next.split("=")[2]
    await send_titles(titles, query, cache_time=1, next_offset=next)


@dp.inline_handler(lambda query: query.query.startswith("#shik_animserial"), state="*")
async def inline_handler(query: types.InlineQuery):
    if query.offset:
        titles, next = await anime_searcher.load_next_page(query.offset)
    else:
        titles, next = await anime_searcher.load_anime(
            types="anime-serial", sort="shikimori_rating"
        )
    if next:
        next = next.split("=")[2]
    await send_titles(titles, query, cache_time=1, next_offset=next)


@dp.inline_handler(lambda query: query.query.startswith("#link_animserial"), state="*")
async def inline_handler(query: types.InlineQuery):
    link = str(query.query).strip().lower()[12:]
    if "imdb.com" in link:
        titles = await anime_searcher.search_imdb_id(link, types="anime-serial")
    elif "kinopoisk.ru" in link:
        titles = await anime_searcher.search_kinopoisk_id(link, types="anime-serial")
    elif "shikimori.one" in link:
        titles = await anime_searcher.search_shikimori_id(link, types="anime-serial")
    else:
        titles = []
    await send_titles(titles, query)


@dp.inline_handler(lambda query: query.query.startswith("#serial"), state="*")
async def inline_handler(query: types.InlineQuery):
    if query.offset:
        titles, next = await films_searcher.load_next_page(query.offset)
    else:
        titles, next = await films_searcher.search(
            phraze=str(query.query).strip().lower()[7:], types="serials"
        )
    if next:
        next = next.split("?")[1].replace("&token=404c284ad24e337a0334c93a837edcec", "")
    await send_titles(titles, query, cache_time=1, next_offset=next)


@dp.inline_handler(lambda query: query.query.startswith("#link_serial"), state="*")
async def inline_handler(query: types.InlineQuery):
    link = str(query.query).strip().lower()[12:]
    if "imdb.com" in link:
        titles = await films_searcher.search_imdb_id(link, types="serials")
    elif "kinopoisk.ru" in link:
        titles = await films_searcher.search_kinopoisk_id(link, types="serials")
    elif "world-art.ru" in link:
        titles = await films_searcher.search_world_art_id(link, types="serials")
    else:
        titles = []
    await send_titles(titles, query)


@dp.inline_handler(lambda query: query.query.startswith("#mulserial"), state="*")
async def inline_handler(query: types.InlineQuery):
    if query.offset:
        titles, next = await films_searcher.load_next_page(query.offset)
    else:
        titles, next = await films_searcher.search(
            phraze=str(query.query).strip().lower()[11:], types="cartoon-serials"
        )
    if next:
        next = (
            next.split("?")[1]
            .replace("&token=404c284ad24e337a0334c93a837edcec", "")
            .replace("&", "_")
        )
    await send_titles(titles, query, cache_time=1, next_offset=next)


@dp.inline_handler(lambda query: query.query.startswith("#link_mulserial"), state="*")
async def inline_handler(query: types.InlineQuery):
    link = str(query.query).strip().lower()[16:]
    if "imdb.com" in link:
        titles = await films_searcher.search_imdb_id(link, types="cartoon-serials")
    elif "kinopoisk.ru" in link:
        titles = await films_searcher.search_kinopoisk_id(link, types="cartoon-serials")
    elif "world-art.ru" in link:
        titles = await films_searcher.search_world_art_id(link, types="cartoon-serials")
    else:
        titles = []
    await send_titles(titles, query)


@dp.inline_handler(lambda query: query.query.startswith("#mult"), state="*")
async def inline_handler(query: types.InlineQuery):
    if query.offset:
        titles, next = await films_searcher.load_next_page(query.offset)
    else:
        titles, next = await films_searcher.search(
            phraze=str(query.query).strip().lower()[6:], types="cartoon"
        )
    if next:
        next = (
            next.split("?")[1]
            .replace("&token=404c284ad24e337a0334c93a837edcec", "")
            .replace("&", "_")
        )
    await send_titles(titles, query, cache_time=1, next_offset=next)


@dp.inline_handler(lambda query: query.query.startswith("#link_mult"), state="*")
async def inline_handler(query: types.InlineQuery):
    link = str(query.query).strip().lower()[9:]
    if "imdb.com" in link:
        titles = await films_searcher.search_imdb_id(link, types="cartoon")
    elif "kinopoisk.ru" in link:
        titles = await films_searcher.search_kinopoisk_id(link, types="cartoon")
    elif "world-art.ru" in link:
        titles = await films_searcher.search_world_art_id(link, types="cartoon")
    else:
        titles = []
    await send_titles(titles, query)


@dp.inline_handler(lambda query: query.query.startswith("#movie"), state="*")
async def inline_handler(query: types.InlineQuery):
    if query.offset:
        titles, next = await films_searcher.load_next_page(query.offset)
    else:
        titles, next = await films_searcher.search(
            phraze=str(query.query).strip().lower()[6:], types="films"
        )
    if next:
        next = (
            next.split("?")[1]
            .replace("&token=404c284ad24e337a0334c93a837edcec", "")
            .replace("&", "_")
        )
    await send_titles(titles, query, cache_time=60, next_offset=next)


@dp.inline_handler(lambda query: query.query.startswith("#link_movie"), state="*")
async def inline_handler(query: types.InlineQuery):
    link = str(query.query).strip().lower()[10:]
    if "imdb.com" in link:
        titles = await films_searcher.search_imdb_id(link, types="films")
    elif "kinopoisk.ru" in link:
        titles = await films_searcher.search_kinopoisk_id(link, types="films")
    elif "world-art.ru" in link:
        titles = await films_searcher.search_world_art_id(link, types="films")
    else:
        titles = []
    await send_titles(titles, query)


@dp.message_handler(text="🔎 Найти сериал")
async def search_animeserial(message):
    await message.delete()
    await message.answer(
        """Поиск
    
    Здесь вы можете выбрать:

    Поиск по названию - просто вводим название сериала

    Кинопоиск, Imdb, Shikimori - лучшие сериалы по версии 
    одной из этих площадок

    Поиск по ссылке - нужно прислать ссылку на сериал с
    <a href="www.kinopoisk.ru">Кинопоиска</a>, <a href="www.imdb.com">Imdb</a> или <a href="shikimori.one">Shikimori</a>""",
        reply_markup=search_anime_series_keyboard,
        parse_mode="html",
        disable_web_page_preview=True,
    )


@dp.message_handler(text="🔎 Найти мультик")
async def search_animemult(message):
    await message.delete()
    await message.answer(
        """Поиск
    
    Здесь вы можете выбрать:

    Поиск по названию - просто вводим название аниме

    Кинопоиск, Imdb, Shikimori - лучшие аниме по версии
    одной из этих площадок

    Поиск по ссылке - нужно прислать ссылку на аниме с
    <a href="www.kinopoisk.ru">Кинопоиска</a>, <a href="www.imdb.com">Imdb</a> или <a href="shikimori.one">Shikimori</a>""",
        reply_markup=search_anime_keyboard,
        parse_mode="html",
        disable_web_page_preview=True,
    )


@dp.message_handler(text="🔎 Мульты")
async def search_mult(message):
    await message.delete()
    await message.answer(
        """Поиск
    
    Здесь вы можете выбрать:

    Поиск по названию - просто вводим название мультфильма

    Поиск по ссылке - нужно прислать ссылку на мультфильм с
    <a href="www.kinopoisk.ru">Кинопоиска</a>, <a href="www.imdb.com">Imdb</a> или <a href="world-art.ru">World_art</a>""",
        reply_markup=search_mult_keyboard,
        parse_mode="html",
        disable_web_page_preview=True,
    )


@dp.message_handler(text="🔎 Фильмы")
async def search_movie(message):
    await message.delete()
    await message.answer(
        """Поиск
    
    Здесь вы можете выбрать:

    Поиск по названию - просто вводим название фильма

    Поиск по ссылке - нужно прислать ссылку на фильм с
    <a href="www.kinopoisk.ru">Кинопоиска</a>, <a href="www.imdb.com">Imdb</a> или <a href="world-art.ru">World_art</a>""",
        reply_markup=search_movie_keyboard,
        parse_mode="html",
        disable_web_page_preview=True,
    )


@dp.message_handler(text="🔎 Мультсерии")
async def search_series(message):
    await message.delete()
    await message.answer(
        """Поиск
    
    Здесь вы можете выбрать:

    Поиск по названию - просто вводим название мульт-сериала

    Поиск по ссылке - нужно прислать ссылку на мульт-сериал с
    <a href="www.kinopoisk.ru">Кинопоиска</a>, <a href="www.imdb.com">Imdb</a> или <a href="world-art.ru">World_art</a>""",
        reply_markup=search_multseries_keyboard,
        parse_mode="html",
        disable_web_page_preview=True,
    )


@dp.message_handler(text="🔎 Сериалы")
async def search_series(message):
    await message.delete()
    await message.answer(
        """Поиск
    
    Здесь вы можете выбрать:

    Поиск по названию - просто вводим название сериала

    Поиск по ссылке - нужно прислать ссылку на сериал с
    <a href="www.kinopoisk.ru">Кинопоиска</a>, <a href="www.imdb.com">Imdb</a> или <a href="world-art.ru">World_art</a>""",
        reply_markup=search_series_keyboard,
        parse_mode="html",
        disable_web_page_preview=True,
    )


@dp.message_handler(text="⭐ Избранное")
async def favorite(message):
    chat_id = message.chat.id
    await message.delete()
    fav_keyboard = InlineKeyboardMarkup(resize_keyboard=True).add(
        InlineKeyboardButton(
            text="Перейти к любимому", switch_inline_query_current_chat="#fav "
        )
    )
    await bot.send_message(
        chat_id=chat_id,
        text="*Избранное* \n\nЗдесь вы можете найти свои отложенные тайтлы",
        parse_mode="Markdown",
        reply_markup=fav_keyboard,
    )


@dp.message_handler(text="🆕 Новинки аниме")
async def new_anime(message):
    chat_id = message.chat.id
    await message.delete()
    await bot.send_message(
        chat_id,
        "*Новинки* \n\nПоказать последние тайты?",
        reply_markup=new_keyboard_anime,
        parse_mode="Markdown",
    )


@dp.message_handler(text="🎥​ К кино")
async def to_kino(message):
    chat_id = message.chat.id
    await message.delete()
    await bot.send_message(
        chat_id,
        "*Фильмы* \n\n Все кинокартины здесь!",
        reply_markup=all_kino_keyb,
        parse_mode="Markdown",
    )


@dp.message_handler(text="🍥 К аниме")
async def to_anime(message):
    chat_id = message.chat.id
    await message.delete()
    await bot.send_message(
        chat_id,
        "*Аниме* \n\n Все аниме здесь!",
        reply_markup=all_anime_keyb,
        parse_mode="Markdown",
    )


@dp.message_handler(text="🆕 Новинки кино")
async def new_films(message):
    chat_id = message.chat.id
    await message.delete()
    await bot.send_message(
        chat_id,
        "*Новинки* \n\nПоказать последние фильмы?",
        reply_markup=new_keyboard_films,
        parse_mode="Markdown",
    )


@dp.message_handler(text="⚙ Настройки")
async def settings(message):
    user_id = message.chat.id
    db_sess = db_session.create_session()
    subscribtion = db_sess.query(Users).get(user_id).notifications
    films = db_sess.query(Users).get(user_id).films
    db_sess.close()
    settings_keyboard = generate_inline_keyboard(
        ["✅ Включить уведомления", "subscribe"]
    )
    if subscribtion:
        settings_keyboard = generate_inline_keyboard(
            ["❌ Выключить уведомления", "unsubscribe"]
        )
    await bot.send_message(
        user_id,
        "*Настройки* \n\nЗдесь вы можете выключить уведомления о новых сериях своих любимых тайтлов",
        reply_markup=settings_keyboard,
        parse_mode="Markdown",
    )
    # if films:
    #     settings_keyboard=generate_inline_keyboard(['Убрать фильмы', 'remove_films'])
    # else:
    #     settings_keyboard=generate_inline_keyboard(['Показать фильмы', 'show_films'])
    # await bot.send_message(user_id,'После включения или выключения функции фильмы, потребуется перезапустить бота командой /start',reply_markup=settings_keyboard)


@dp.message_handler(text="8956")
async def favorite(message):
    chat_id = message.chat.id
    await message.delete()
    await FormMessage.text.set()
    await bot.send_message(
        chat_id,
        'Введите текст сообщения, "skip" для пропуска',
        reply_markup=InlineKeyboardMarkup(resize_keyboard=True).add(
            InlineKeyboardButton(text="Пропустить", callback_data="skip text")
        ),
    )


@dp.message_handler(state=FormMessage.text)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text.strip() != "skip":
            data["text"] = message.text
        else:
            data["text"] = ""
    await FormMessage.next()
    await message.answer('Отправьте картинку к посту, "skip" для пропуска')


@dp.message_handler(state=FormMessage.photo, content_types=["photo"])
async def process_photo(message: types.Message, state: FSMContext):
    if message.caption:
        if message.caption.strip() == "skip":
            async with state.proxy() as data:
                data["photo"] = ""
        else:
            await message.answer("Команда не распознана")
            return
    else:
        async with state.proxy() as data:
            data["photo"] = message.photo[-1].file_id
    await FormMessage.next()
    await message.answer(
        """Добавте кнопки к посту. Пример:

                            Кнопка 1 - https://youtube.com
                            Кнопка 2 - vk.com

                            "skip" для пропуска""",
        disable_web_page_preview=True,
    )


@dp.message_handler(state=FormMessage.Features)
async def process_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text.strip() != "skip":
            data["buttons"] = message.text
        else:
            async with state.proxy() as data:
                data["buttons"] = ""
        await message.answer(
            "Превью сообщения, напишите ok для отправки, cancel для отмены"
        )
        await FormMessage.next()
        if data["photo"]:
            if data["buttons"]:
                keyb = prepare_spam_keyb(data)
                await bot.send_photo(
                    message.chat.id, data["photo"], data["text"], reply_markup=keyb
                )
            else:
                await bot.send_photo(message.chat.id, data["photo"], data["text"])
        else:
            if data["buttons"]:
                keyb = prepare_spam_keyb(data)
                await bot.send_message(message.chat.id, data["text"], reply_markup=keyb)
            else:
                await bot.send_message(message.chat.id, data["text"])


def prepare_spam_keyb(data):
    buttons = []
    strings = data["buttons"].split("\n")
    for string in strings:
        button_data = string.split("-")
        buttons.append([button_data[0].strip(), button_data[1].strip()])
    return generate_inline_link_keyboard(buttons)


@dp.message_handler(state=FormMessage.answer)
async def final_form(message: types.Message, state: FSMContext):
    if message.text.strip() == "ok":
        db_sess = db_session.create_session()
        users = [db_sess.query(Users).get(631874013)]
        async with state.proxy() as data:
            await mail(data, users)
        await message.answer("Успешно разослано")
        await state.finish()
    elif message.text.strip() == "cancel":
        await state.finish()
        await message.answer("Успешно отменено")
    else:
        await message.answer("Ответ не распознан, повторите")


async def mail(data, users):
    if data["photo"]:
        if data["buttons"]:
            keyb = prepare_spam_keyb(data)
            for user in users:
                try:
                    await bot.send_photo(
                        user.id, data["photo"], data["text"], reply_markup=keyb
                    )
                except Exception:
                    pass
        else:
            for user in users:
                try:
                    await bot.send_photo(user.id, data["photo"], data["text"])
                except Exception:
                    pass
    else:
        if data["buttons"]:
            keyb = prepare_spam_keyb(data)
            for user in users:
                try:
                    await bot.send_message(user.id, data["text"], reply_markup=keyb)
                except Exception:
                    pass
        else:
            for user in users:
                try:
                    await bot.send_message(user.id, data["text"])
                except Exception:
                    pass


async def unsubscribe(call):
    await bot.edit_message_reply_markup(
        call.from_user.id,
        call.message.message_id,
        reply_markup=generate_inline_keyboard(["✅ Включить уведомления", "subscribe"]),
    )
    await call.answer("Вы успешно отключили уведомления")
    user_id = call.message.chat.id
    db_sess = db_session.create_session()
    user = db_sess.query(Users).get(user_id)
    user.notifications = False
    db_sess.commit()
    db_sess.close()


async def subscribe(call):
    await bot.edit_message_reply_markup(
        call.from_user.id,
        call.message.message_id,
        reply_markup=generate_inline_keyboard(
            ["❌ Выключить уведомления", "unsubscribe"]
        ),
    )
    await call.answer("Вы успешно включили уведомления")
    user_id = call.message.chat.id
    db_sess = db_session.create_session()
    user = db_sess.query(Users).get(user_id)
    user.notifications = True
    db_sess.commit()
    db_sess.close()


async def cancell(call):
    await call.answer("Отменено")
    await cancel_handler()


commands = {
    "unsubscribe": unsubscribe,
    "subscribe": subscribe,
    "skip": unsubscribe,
    "remove_from_favorites": remove_from_favorites,
    "add_to_favorites": add_to_favorites,
    "remove_films": remove_films,
    "show_films": show_films,
}


@dp.callback_query_handler(lambda call: True)
async def ans(call):
    await commands[call.data.split()[0]](call)


# def timer_sending(bot,loop):
#     asyncio.run_coroutine_threadsafe(photo_sender(bot),loop)
#     time.sleep(10)

# schedule.every().day.at('06:54').do(lambda: timer_sending(bot,loop))
# def schedule_cycle():
#     while True:
#         schedule.run_pending()
#         time.sleep(1)


async def main():
    for admin in admins:
        await bot.send_message(admin, "Bot started")
    await dp.start_polling()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    asyncio.run(main())
