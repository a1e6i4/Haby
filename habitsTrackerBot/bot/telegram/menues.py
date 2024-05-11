from abc import ABC, abstractmethod

import telebot

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from .templates import *
from .utils import create_markup


class BaseView(ABC):
    @abstractmethod
    def mount(self, *args, **kwargs):
        raise NotImplementedError

    def render(self, bot: telebot.TeleBot, chat_id, caption, reply_markup=None, modify=False,
               message_to_modify: telebot.types.Message = None):
        if not modify:
            bot.send_message(chat_id, caption, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            bot.edit_message_text(caption, chat_id, message_to_modify.message_id,
                                  reply_markup=reply_markup, parse_mode='Markdown')


class MainMenu(BaseView):
    def mount(self, bot, user_id, chat_id, message=None, *args, **kwargs):
        self.render(bot, chat_id, main_menu_template, reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🔄 Привычки", callback_data="habits")],
                [InlineKeyboardButton("🏆 Достижения", callback_data="achievements")],
            ]
        ), modify=message is not None, message_to_modify=message)


class HabitsListMenu(BaseView):
    def mount(self, bot: telebot.TeleBot, user_id, chat_id, message=None, *args, **kwargs):
        habits = list(bot.looser.habits.all())
        markup = create_markup([habit.name for habit in habits], [f"habit_{habit.id}" for habit in habits])
        markup.keyboard.append([InlineKeyboardButton("🔄 Завести привычку", callback_data="add_habit")])
        markup.keyboard.append([InlineKeyboardButton("<< Назад", callback_data="back_main_menu")])

        self.render(bot, chat_id, "Выберите привычку", reply_markup=markup, modify=message is not None,
                    message_to_modify=message)


class HabitActionsMenu(BaseView):
    def mount(self, bot, user_id, chat_id, habit, message=None, *args, **kwargs):
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("➕ Добавить запись", callback_data=f"add_value_h_{habit.id}")],
                [InlineKeyboardButton("📊 Посмотреть статистику", callback_data=f"show_progress_h_{habit.id}")],
                [InlineKeyboardButton("❌ Удалить", callback_data=f"delete_h_{habit.id}")],
                [InlineKeyboardButton("<< Назад к списку привычек", callback_data="back_h_list")]
            ]

        )
        self.render(bot, chat_id, habit_action_template.format(habit.name), reply_markup=reply_markup,
                    modify=message is not None, message_to_modify=message)


class HabitShowStatMenu(BaseView):
    def mount(self, bot, user_id, chat_id, habit, message=None, *args, **kwargs):
        caption = habit_stat_period_choice_template.format(habit.name)
        markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("📅 За неделю", callback_data=f"week_h_{habit.id}")],
                [InlineKeyboardButton("🗓️ За месяц", callback_data=f"month_h_{habit.id}")],
                [InlineKeyboardButton("🕰️ За все время", callback_data=f"all_time_h_{habit.id}")],
                [InlineKeyboardButton("<< Назад", callback_data=f"habit_{habit.id}")]
            ]

        )

        self.render(bot, chat_id, caption, reply_markup=markup, modify=message is not None,
                    message_to_modify=message)


class HabitDeleteConfirmMenu(BaseView):
    def mount(self, bot, user_id, chat_id, habit, message=None, *args, **kwargs):
        caption = f"Вы уверены, что хотите удалить привычку «{habit.name}»?"
        markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Да", callback_data=f"delete_confirm_h_{habit.id}")],
             [InlineKeyboardButton("<< Назад", callback_data=f"habit_{habit.id}")]]
        )

        self.render(bot, chat_id, caption, reply_markup=markup, modify=message is not None,
                    message_to_modify=message)


class HabitDeletedMenu(BaseView):
    def mount(self, bot, user_id, chat_id, message=None, *args, **kwargs):
        self.render(bot, chat_id, kwargs['caption'], reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("<< Назад к списку привычек", callback_data="back_h_list")]]
        ), modify=True, message_to_modify=message)


# Achievements

class AchievementsListMenu(BaseView):
    def mount(self, bot, user_id, chat_id, message=None, *args, **kwargs):
        ach_lists = list(bot.looser.achievement_lists.all())
        markup = create_markup([ach_list.name for ach_list in ach_lists],
                               [f"ach_list_{ach_list.id}" for ach_list in ach_lists])
        markup.keyboard.append([InlineKeyboardButton("🎖️📝 Создать список", callback_data="add_ach_list")])
        markup.keyboard.append([InlineKeyboardButton("<< Назад", callback_data="back_main_menu")])

        self.render(bot, chat_id, "Выберите список достижений", reply_markup=markup, modify=message is not None,
                    message_to_modify=message)


class AchievementsListActionMenu(BaseView):
    def mount(self, bot, user_id, chat_id, ach_list, message=None, *args, **kwargs):
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("➕ Добавить достижение", callback_data=f"add_ach_al_{ach_list.id}")],
                [InlineKeyboardButton("📝 Посмотреть достижения", callback_data=f"show_ach_al_{ach_list.id}")],
                [InlineKeyboardButton("❌ Удалить", callback_data=f"delete_al_{ach_list.id}")],
                [InlineKeyboardButton("<< Назад к спискам", callback_data="back_al_lists")]
            ]

        )
        self.render(bot, chat_id, ach_list_action_template.format(ach_list.name), reply_markup=reply_markup,
                    modify=message is not None, message_to_modify=message)


class AchievementShowStatMenu(BaseView):
    def mount(self, bot, user_id, chat_id, ach_list, message=None, *args, **kwargs):
        caption = ach_stat_period_choice_template.format(ach_list.name)
        markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("📅 За неделю", callback_data=f"week_al_{ach_list.id}")],
                [InlineKeyboardButton("🗓️ За месяц", callback_data=f"month_al_{ach_list.id}")],
                [InlineKeyboardButton("🕰️ За все время", callback_data=f"all_time_al_{ach_list.id}")],
                [InlineKeyboardButton("<< Назад", callback_data=f"ach_list_{ach_list.id}")]
            ]

        )

        self.render(bot, chat_id, caption, reply_markup=markup, modify=message is not None,
                    message_to_modify=message)


class AchievementListDeleteConfirmMenu(BaseView):
    def mount(self, bot, user_id, chat_id, ach_list, message=None, *args, **kwargs):
        caption = f"Вы уверены, что хотите удалить список достижений «{ach_list.name}»?"
        markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Да", callback_data=f"delete_confirm_al_{ach_list.id}")],
             [InlineKeyboardButton("<< Назад", callback_data=f"ach_list_{ach_list.id}")]]
        )

        self.render(bot, chat_id, caption, reply_markup=markup, modify=message is not None,
                    message_to_modify=message)


class AchievementListDeletedMenu(BaseView):
    def mount(self, bot, user_id, chat_id, message=None, *args, **kwargs):
        self.render(bot, chat_id, kwargs['caption'], reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("<< Назад к спискам достижений", callback_data="back_al_lists")]]
        ), modify=True, message_to_modify=message)
