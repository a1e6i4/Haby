from telebot.handler_backends import State, StatesGroup


class HabitStates(StatesGroup):
    habit_name = State()
    habit_unit = State()
    habit_show_template = State()

    habit_insert = State()
    ach_list_name = State()
    achievement_description = State()
