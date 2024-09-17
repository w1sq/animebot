from aiogram.types import (
    InputTextMessageContent,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InlineQueryResultPhoto,
)
from aiogram.types.inline_query_result import InlineQueryResultArticle
from db_data import db_session
from db_data.__all_models import Users, Anime
from uuid import uuid4


async def add_to_favorites(call):
    await call.answer("Добавлено в избранное")
    user_id = call.from_user.id
    id = call.data.split()[1]
    db_sess = db_session.create_session()
    anime = db_sess.query(Anime).filter(Anime.kodik_id == id).first()
    user = db_sess.query(Users).get(user_id)
    user.favorites.append(anime)
    db_sess.commit()
    db_sess.close()


async def remove_from_favorites(call):
    await call.answer("Удалено из избранных")
    id = call.data.split()[1]
    db_sess = db_session.create_session()
    anime = db_sess.query(Anime).filter(Anime.kodik_id == id).first()
    user = db_sess.query(Users).get(call.from_user.id)
    user.favorites.remove(anime)
    db_sess.commit()
    db_sess.close()


async def remove_films(call):
    await call.answer("Фильмы спрятаны")
    await call.message.answer(
        "После включения или выключения функции фильмы, потребуется перезапустить бота командой /start"
    )
    db_sess = db_session.create_session()
    user = db_sess.query(Users).get(call.from_user.id)
    user.films = False
    db_sess.commit()
    db_sess.close()


async def show_films(call):
    await call.answer("Фильмы появились")
    await call.message.answer(
        "После включения или выключения функции фильмы, потребуется перезапустить бота командой /start"
    )
    db_sess = db_session.create_session()
    user = db_sess.query(Users).get(call.from_user.id)
    user.films = True
    db_sess.commit()
    db_sess.close()


def uuid5():
    return str(uuid4())


async def send_titles(
    titles,
    query,
    cache_time=1,
    text="✅ Добавить в понравившиеся",
    callback_data="add_to_favorites",
    next_offset="",
):
    results = []
    for num, i in enumerate(titles):
        try:
            results.append(
                InlineQueryResultArticle(
                    id=uuid5(),
                    title=i.title,
                    thumb_url=i.poster_link,
                    description=f"{i.imdb_rating} {i.kinopoisk_rating}\n{i.year}",
                    reply_markup=InlineKeyboardMarkup(resize_keyboard=True)
                    .add(
                        InlineKeyboardButton(
                            text="🍿 Смотреть",
                            url=f"https://bot.animepoint.cc/id/{i.kodik_id}",
                        )
                    )
                    .add(
                        InlineKeyboardButton(
                            text=text, callback_data=f"{callback_data} {i.kodik_id}"
                        )
                    )
                    .add(
                        InlineKeyboardButton(
                            text="🔎 Поиск по названию",
                            switch_inline_query_current_chat="#all ",
                        )
                    ),
                    # reply_markup=InlineKeyboardMarkup(resize_keyboard=True).add(InlineKeyboardButton(text='🍿 Смотреть',url=f'http://45.147.198.210:5000/id/{i.kodik_id}')).add(InlineKeyboardButton(text=text,callback_data=f'{callback_data}#{i.kodik_id}')).add(InlineKeyboardButton(text='🔎 Поиск по названию',switch_inline_query_current_chat="#all ")),
                    input_message_content=InputTextMessageContent(
                        message_text=i.to_message(), parse_mode="html"
                    ),
                )
            )
        except Exception:
            results.append(
                InlineQueryResultArticle(
                    id=uuid5(),
                    title=i.title,
                    thumb_url=i.poster_link,
                    description=f"{i.imdb_rating} {i.kinopoisk_rating}\n{i.year}",
                    reply_markup=InlineKeyboardMarkup(resize_keyboard=True)
                    .add(
                        InlineKeyboardButton(
                            text="🍿 Смотреть",
                            url=f"https://bot.animepoint.cc/id/{i.kodik_id}",
                        )
                    )
                    .add(
                        InlineKeyboardButton(
                            text=text, callback_data=f"{callback_data} {i.kodik_id}"
                        )
                    )
                    .add(
                        InlineKeyboardButton(
                            text="🔎 Поиск по названию",
                            switch_inline_query_current_chat="#all ",
                        )
                    ),
                    # reply_markup=InlineKeyboardMarkup(resize_keyboard=True).add(InlineKeyboardButton(text='🍿 Смотреть',url=f'http://45.147.198.210:5000/id/{i.kodik_id}')).add(InlineKeyboardButton(text=text,callback_data=f'{callback_data}#{i.kodik_id}')).add(InlineKeyboardButton(text='🔎 Поиск по названию',switch_inline_query_current_chat="#all ")),
                    input_message_content=InputTextMessageContent(
                        message_text=i.to_message(), parse_mode="html"
                    ),
                )
            )

    if query and not results:
        results.append(
            InlineQueryResultArticle(
                id=uuid5(),
                title="Ничего не нашлось",
                thumb_url="https://котовчанин.рф/content/uploads/2017/10/stranica-ne-naydena.jpeg",
                input_message_content=InputTextMessageContent(
                    message_text=f"Ничего не нашлось",
                ),
            )
        )
    await query.answer(
        results=results,
        cache_time=cache_time,
        switch_pm_text="Перейти в бот",
        switch_pm_parameter="start",
        next_offset=next_offset,
    )
