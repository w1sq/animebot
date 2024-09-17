from aiogram.dispatcher.filters.state import State, StatesGroup


class FormLinkSearchAnime(StatesGroup):
    answer = State()


class FormLinkSearchSeries(StatesGroup):
    answer = State()


class FormNameSearchAnime(StatesGroup):
    answer = State()


class FormNameSearchSeries(StatesGroup):
    answer = State()


class FormMessage(StatesGroup):
    text = State()
    photo = State()
    Features = State()
    answer = State()
