from aiogram.types import (
    InputTextMessageContent,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InlineQueryResultPhoto,
)


def generate_keyboard(*answer):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    temp_buttons = []
    for i in answer:
        temp_buttons.append(KeyboardButton(text=i))
    keyboard.add(*temp_buttons)
    return keyboard


def generate_inline_keyboard(*answer):
    keyboard = InlineKeyboardMarkup()
    temp_buttons = []
    for i in answer:
        temp_buttons.append(InlineKeyboardButton(text=str(i[0]), callback_data=i[1]))
    keyboard.add(*temp_buttons)
    return keyboard


def generate_inline_link_keyboard(answer):
    keyboard = InlineKeyboardMarkup()
    temp_buttons = []
    for i in answer:
        temp_buttons.append(InlineKeyboardButton(text=str(i[0]), url=str(i[1])))
    keyboard.add(*temp_buttons)
    return keyboard
