from telebot import TeleBot, custom_filters
from django.db import connection
from telebot.types import BotCommand

from .middleware import AuthMiddleware
from .handlers import *
from .states import HabitStates


class HabitsBot(TeleBot):
    def __init__(self, token, state_storage=None):
        super().__init__(token, state_storage, use_class_middlewares=True)

        self.setup_middleware(AuthMiddleware(self))
        self.register_handlers()
        self.add_custom_filter(custom_filters.StateFilter(self))

        self.set_my_commands([
            BotCommand('start', 'Нажмите чтобы  начать'),
        ])

        self.looser = None

    def __enter__(self):
        connection.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        connection.close()

    def register_handlers(self):
        self.register_message_handler(handle_recommend_habit, commands=['recommend'], pass_bot=True)
        self.register_message_handler(handle_retrain, commands=['retrain'], pass_bot=True)
        self.register_message_handler(handle_start, commands=['start'], pass_bot=True)
        self.register_callback_query_handler(handle_show_habits, func=lambda call: call.data == 'habits', pass_bot=True)
        self.register_callback_query_handler(handle_back_main_menu, func=lambda call: call.data == 'back_main_menu',
                                             pass_bot=True)

        self.register_callback_query_handler(handle_add_habit, func=lambda call: call.data.startswith('add_habit'),
                                             pass_bot=True)

        self.register_message_handler(handle_add_habit_name, state=HabitStates.habit_name, pass_bot=True)
        self.register_message_handler(handle_add_habit_unit, state=HabitStates.habit_unit, pass_bot=True)
        self.register_message_handler(handle_add_habit_show_template, state=HabitStates.habit_show_template,
                                      pass_bot=True)

        self.register_callback_query_handler(handle_choice_habit, func=lambda call: call.data.startswith('habit_'),
                                             pass_bot=True)
        self.register_callback_query_handler(handle_habit_add_value,
                                             func=lambda call: call.data.startswith('add_value_h_'),
                                             pass_bot=True)
        self.register_message_handler(handle_insert_habit_value, state=HabitStates.habit_insert, pass_bot=True)
        self.register_callback_query_handler(handle_habit_delete, func=lambda call: call.data.startswith('delete_h_'),
                                             pass_bot=True)
        self.register_callback_query_handler(handle_habit_show_progress,
                                             func=lambda call: call.data.startswith('show_progress_h_'),
                                             pass_bot=True)
        self.register_callback_query_handler(handle_show_progress,
                                             func=lambda call: call.data.startswith('week_h_') or call.data.startswith(
                                                 'month_h_') or call.data.startswith('all_time_h_'),
                                             pass_bot=True)
        self.register_callback_query_handler(handle_habit_delete, func=lambda call: call.data.startswith('delete_h_'),
                                             pass_bot=True)

        self.register_callback_query_handler(handle_delete_habit_confirm,
                                             func=lambda call: call.data.startswith('delete_confirm_h_'),
                                             pass_bot=True)

        self.register_callback_query_handler(handle_back_to_habit_list, func=lambda call: call.data == 'back_h_list',
                                             pass_bot=True)

        # Achievements
        self.register_callback_query_handler(handle_show_achievements, func=lambda call: call.data == 'achievements',
                                             pass_bot=True)
        self.register_callback_query_handler(handle_add_ach_list, func=lambda call: call.data == 'add_ach_list',
                                             pass_bot=True)
        self.register_message_handler(handle_add_ach_list_name, state=HabitStates.ach_list_name, pass_bot=True,
                                      func=lambda message: True)

        self.register_callback_query_handler(handle_back_al_lists, func=lambda call: call.data == 'back_al_lists',
                                             pass_bot=True)

        self.register_callback_query_handler(handle_add_achievement, pass_bot=True,
                                             func=lambda call: call.data.startswith('add_ach_al_'))

        self.register_message_handler(handle_add_achievement_description, state=HabitStates.achievement_description,
                                      pass_bot=True)

        self.register_callback_query_handler(handle_choice_al, func=lambda call: call.data.startswith('ach_list_'),
                                             pass_bot=True)

        self.register_callback_query_handler(handle_show_achievement_progress,
                                             func=lambda call: call.data.startswith('show_ach_al_'),
                                             pass_bot=True)

        self.register_callback_query_handler(handle_choose_achievement_period,
                                             func=lambda call: call.data.startswith('week_al_') or call.data.startswith(
                                                 'month_al_') or call.data.startswith('all_time_al_'),
                                             pass_bot=True)

        self.register_callback_query_handler(handle_al_delete, func=lambda call: call.data.startswith('delete_al_'),
                                             pass_bot=True)

        self.register_callback_query_handler(handle_delete_al_confirm, func=lambda call: call.data.startswith('delete_confirm_al_'),
                                             pass_bot=True)
