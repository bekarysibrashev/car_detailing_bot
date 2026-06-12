from aiogram.fsm.state import State, StatesGroup


class CarState(StatesGroup):
    waiting_photo   = State()
    waiting_color   = State()
    waiting_coating = State()
    generating      = State()