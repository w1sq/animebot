from aiogram.types import (
    InputTextMessageContent,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


all_anime_keyb = (
    ReplyKeyboardMarkup(resize_keyboard=True)
    .row(KeyboardButton("🔎 Найти сериал"), KeyboardButton("🔎 Найти мультик"))
    .row(KeyboardButton("🆕 Новинки аниме"), KeyboardButton("⭐ Избранное"))
    .row(KeyboardButton("🎥​ К кино"))
    .row(KeyboardButton("⚙ Настройки"))
)


search_anime_series_keyboard = (
    InlineKeyboardMarkup(resize_keyboard=True)
    .row(
        InlineKeyboardButton(
            text="🔠 Название", switch_inline_query_current_chat="#animserial "
        ),
    )
    .row(
        InlineKeyboardButton(
            text="🔎 Кинопоиск", switch_inline_query_current_chat="#kinp_animserial "
        ),
        InlineKeyboardButton(
            text="🔎 IMDB", switch_inline_query_current_chat="#imd_animserial "
        ),
        InlineKeyboardButton(
            text="🔎 Shikimori", switch_inline_query_current_chat="#shik_animserial "
        ),
    )
    .row(
        InlineKeyboardButton(
            text="🌐 По ссылке", switch_inline_query_current_chat="#link_animserial "
        )
    )
)

search_anime_keyboard = (
    InlineKeyboardMarkup(resize_keyboard=True)
    .row(
        InlineKeyboardButton(
            text="🔠 Название", switch_inline_query_current_chat="#anime "
        )
    )
    .row(
        InlineKeyboardButton(
            text="🔎 Кинопоиск", switch_inline_query_current_chat="#kp_anime "
        ),
        InlineKeyboardButton(
            text="🔎 IMDB", switch_inline_query_current_chat="#imdb_anime "
        ),
        InlineKeyboardButton(
            text="🔎 Shikimori", switch_inline_query_current_chat="#shk_anime "
        ),
    )
    .row(
        InlineKeyboardButton(
            text="🌐 По ссылке", switch_inline_query_current_chat="#link_anime "
        )
    )
)

search_series_keyboard = (
    InlineKeyboardMarkup(resize_keyboard=True)
    .row(
        InlineKeyboardButton(
            text="🔠 Название", switch_inline_query_current_chat="#serial "
        )
    )
    .row(
        InlineKeyboardButton(
            text="🌐 По ссылке", switch_inline_query_current_chat="#link_serial "
        )
    )
)

search_mult_keyboard = (
    InlineKeyboardMarkup(resize_keyboard=True)
    .row(
        InlineKeyboardButton(
            text="🔠 Название", switch_inline_query_current_chat="#mult "
        )
    )
    .row(
        InlineKeyboardButton(
            text="🌐 По ссылке", switch_inline_query_current_chat="#link_mult "
        )
    )
)

search_multseries_keyboard = (
    InlineKeyboardMarkup(resize_keyboard=True)
    .row(
        InlineKeyboardButton(
            text="🔠 Название", switch_inline_query_current_chat="#mulserial "
        )
    )
    .row(
        InlineKeyboardButton(
            text="🌐 По ссылке", switch_inline_query_current_chat="#link_mulserial "
        )
    )
)


search_movie_keyboard = (
    InlineKeyboardMarkup(resize_keyboard=True)
    .row(
        InlineKeyboardButton(
            text="🔠 Название", switch_inline_query_current_chat="#movie "
        )
    )
    .row(
        InlineKeyboardButton(
            text="🌐 По ссылке", switch_inline_query_current_chat="#link_movie "
        )
    )
)

new_keyboard_anime = InlineKeyboardMarkup(resize_keyboard=True).row(
    InlineKeyboardButton(
        text="Показать новинки", switch_inline_query_current_chat="#newanime "
    )
)
new_keyboard_films = InlineKeyboardMarkup(resize_keyboard=True).row(
    InlineKeyboardButton(
        text="Показать новинки", switch_inline_query_current_chat="#newfilms "
    )
)

all_kino_keyb = (
    ReplyKeyboardMarkup(resize_keyboard=True)
    .row(KeyboardButton("🔎 Фильмы"), KeyboardButton("🔎 Сериалы"))
    .row(KeyboardButton("🔎 Мульты"), KeyboardButton("🔎 Мультсерии"))
    .row(KeyboardButton("🆕 Новинки кино"), KeyboardButton("⭐ Избранное"))
    .row(KeyboardButton("🍥 К аниме"), KeyboardButton("⚙ Настройки"))
)
