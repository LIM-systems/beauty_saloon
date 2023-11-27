from aiogram.dispatcher.filters.state import State, StatesGroup


class ClientData(StatesGroup):
    name = State()
    phone = State()
