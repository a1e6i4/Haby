from datetime import datetime, timedelta
from telebot import TeleBot, types
from habits.models import Habit, Goal, AchievementList, Achievement
from .menues import *
from .states import HabitStates
from .templates import *
from .utils import get_show_template, format_number
from ..tasks import retrain_model, recommend_habit


def handle_start(message: types.Message, bot: TeleBot):
    MainMenu().mount(bot, message.from_user.id, message.chat.id)


def handle_back_main_menu(call: types.CallbackQuery, bot: TeleBot):
    MainMenu().mount(bot, call.from_user.id, call.message.chat.id, call.message)


def handle_add_habit(call: types.CallbackQuery, bot: TeleBot):
    bot.set_state(call.from_user.id, HabitStates.habit_name, call.message.chat.id)
    bot.send_message(call.message.chat.id, "Введите название привычки", parse_mode='Markdown')


def handle_add_habit_name(message: types.Message, bot: TeleBot):
    bot.set_state(message.from_user.id, HabitStates.habit_unit, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['habit_name'] = message.text

    bot.send_message(message.chat.id, habit_unit_template, parse_mode='Markdown')


def handle_add_habit_unit(message: types.Message, bot: TeleBot):
    bot.set_state(message.from_user.id, HabitStates.habit_show_template, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['habit_unit'] = message.text

    bot.send_message(message.chat.id, habit_show_template, parse_mode='Markdown')


def handle_add_habit_show_template(message: types.Message, bot: TeleBot):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        Habit.objects.create(
            user=bot.looser,
            name=data['habit_name'],
            unit=data['habit_unit'],
            show_template=get_show_template(message.text)
        )

    bot.send_message(message.chat.id, """Отлично, привычка создана!""", parse_mode='Markdown',
                     reply_markup=InlineKeyboardMarkup(
                         [[InlineKeyboardButton("<< Назад к списку привычек", callback_data="back_h_list")]]
                     ))


'''
def handle_goal_choice(call: types.CallbackQuery, bot: TeleBot):
    if call.data == 'add_goal':
        bot.set_state(call.from_user.id, HabitStates.goal_value, call.message.chat.id)
        bot.send_message(call.message.chat.id, "Сколько? (введите число)", parse_mode='Markdown')
    elif call.data == 'skip_goal':
        MainMenu().mount(bot, call.from_user.id, call.message.chat.id)


def handle_goal_value(message: types.Message, bot: TeleBot):
    bot.set_state(message.from_user.id, HabitStates.goal_date, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['goal_value'] = int(message.text)

    bot.send_message(message.chat.id, """
        Когда дедлайн? (введите дату в формате дд.мм.гггг)
    """, parse_mode='Markdown')


def handle_goal_date(message: types.Message, bot: TeleBot):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['goal_date'] = datetime.strptime(message.text, '%d.%m.%Y')

        goal = Goal.objects.create(
            habit=Habit.objects.get(id=data['habit']),
            value=data['goal_value'],
            deadline=data['goal_date']
        )

    work_per_day = goal.value / (goal.deadline - goal.created_at.replace(tzinfo=None)).days
    bot.send_message(message.chat.id, goal_complete.format(
        goal_value=goal.value,
        habit_unit=goal.habit.unit,
        goal_deadline=goal.deadline.strftime('%d.%m.%Y'),
        habit_name=goal.habit.name,
        work_per_day=round(work_per_day, 2)
    ), parse_mode='Markdown')

    MainMenu().mount(bot, message.from_user.id, message.chat.id)
'''


def handle_show_habits(call: types.CallbackQuery, bot: TeleBot):
    HabitsListMenu().mount(bot, call.from_user.id, call.message.chat.id, call.message)


def handle_choice_habit(call: types.CallbackQuery, bot: TeleBot):
    habit_id = int(call.data.split('_')[-1])

    try:
        habit = Habit.objects.get(id=habit_id)
    except Habit.DoesNotExist:
        bot.answer_callback_query(call.id, "Привычка не найдена", show_alert=True)
        return

    HabitActionsMenu().mount(bot, call.from_user.id, call.message.chat.id, habit, call.message)


def handle_habit_add_value(call: types.CallbackQuery, bot: TeleBot):
    h_id = int(call.data.split('_')[-1])
    try:
        habit = Habit.objects.get(id=h_id)
    except Habit.DoesNotExist:
        bot.answer_callback_query(call.id, "Привычка не найдена", show_alert=True)
        return

    bot.set_state(call.from_user.id, HabitStates.habit_insert, call.message.chat.id)
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['habit'] = habit.id
    bot.send_message(call.message.chat.id, f"Введите значение ({habit.unit})", parse_mode='Markdown')


def handle_insert_habit_value(message: types.Message, bot: TeleBot):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        habit = Habit.objects.get(id=data['habit'])

        try:
            value = float(message.text)
        except ValueError:
            bot.send_message(message.chat.id, "Неверный формат. Введите число", parse_mode='Markdown')
            return

        last_record = habit.records.last()
        habit.records.create(
            value=value,
            cumulative_value=last_record.cumulative_value + value if last_record else value
        )

        bot.delete_state(message.from_user.id, message.chat.id)
        bot.send_message(message.chat.id, habit_value_added.format(
            habit_show_template=habit.show_template.format(value=format_number(value)),
        ), parse_mode='Markdown')


def handle_habit_show_progress(call: types.CallbackQuery, bot: TeleBot):
    h_id = int(call.data.split('_')[-1])
    try:
        habit = Habit.objects.get(id=h_id)
    except Habit.DoesNotExist:
        bot.answer_callback_query(call.id, "Привычка не найдена", show_alert=True)
        return

    HabitShowStatMenu().mount(bot, call.from_user.id, call.message.chat.id, habit, call.message)


def handle_show_progress(call: types.CallbackQuery, bot: TeleBot):
    time_interval = None
    if call.data.startswith('week'):
        time_interval = (datetime.now() - timedelta(days=7), datetime.now())
    elif call.data.startswith('month'):
        time_interval = (datetime.now() - timedelta(days=30), datetime.now())

    h_id = int(call.data.split('_')[-1])
    try:
        habit = Habit.objects.get(id=h_id)
    except Habit.DoesNotExist:
        bot.answer_callback_query(call.id, "Привычка не найдена", show_alert=True)
        return

    records = habit.records
    if time_interval is not None:
        records = records.filter(date__range=time_interval)
    else:
        records = records.all()

    records = list(records)

    if not records:
        bot.send_message(call.message.chat.id, "За этот период нет записей", parse_mode='Markdown')
        return

    time_int_dict = {
        'week': 'последнюю неделю',
        'month': 'последний месяц',
        'all_time': 'все время'
    }

    bot.send_message(call.message.chat.id, habit_stat_template.format(
        time_interval=time_int_dict["_".join(call.data.split('_')[0:-2])],
        habit_show_template=habit.show_template.format(value=format_number(sum([record.value for record in records]))),
    ), parse_mode='Markdown')


def handle_habit_delete(call: types.CallbackQuery, bot: TeleBot):
    h_id = int(call.data.split('_')[-1])
    try:
        habit = Habit.objects.get(id=h_id)
    except Habit.DoesNotExist:
        bot.answer_callback_query(call.id, "Привычка не найдена", show_alert=True)
        return

    HabitDeleteConfirmMenu().mount(bot, call.from_user.id, call.message.chat.id, habit, call.message)


def handle_delete_habit_confirm(call: types.CallbackQuery, bot: TeleBot):
    h_id = int(call.data.split('_')[-1])
    try:
        habit = Habit.objects.get(id=h_id)
    except Habit.DoesNotExist:
        bot.answer_callback_query(call.id, "Привычка не найдена", show_alert=True)
        return

    habit_name = habit.name
    habit.delete()
    HabitDeletedMenu().mount(bot, call.from_user.id, call.message.chat.id, call.message,
                             caption=f"Привычка {habit_name} удалена")


def handle_back_to_habit_list(call: types.CallbackQuery, bot: TeleBot):
    HabitsListMenu().mount(bot, call.from_user.id, call.message.chat.id, call.message)


# Achievements

def handle_show_achievements(call: types.CallbackQuery, bot: TeleBot):
    AchievementsListMenu().mount(bot, call.from_user.id, call.message.chat.id, call.message)


def handle_add_ach_list(call: types.CallbackQuery, bot: TeleBot):
    bot.set_state(call.from_user.id, HabitStates.ach_list_name, call.message.chat.id)
    bot.send_message(call.message.chat.id, "Как называется список достижений?", parse_mode='Markdown')


def handle_add_ach_list_name(message: types.Message, bot: TeleBot):
    ach_list = AchievementList.objects.create(
        user=bot.looser,
        name=message.text
    )

    bot.delete_state(message.from_user.id, message.chat.id)
    bot.send_message(message.chat.id, achievement_list_added.format(
        achievement_list_description=ach_list.name),
                     parse_mode='Markdown',
                     reply_markup=InlineKeyboardMarkup(
                         [[InlineKeyboardButton("Добвить достижение", callback_data=f"add_ach_al_{ach_list.id}")],
                          [InlineKeyboardButton("<< Назад к спискам достижений", callback_data="back_al_lists")]]
                     ))


def handle_back_al_lists(call: types.CallbackQuery, bot: TeleBot):
    AchievementsListMenu().mount(bot, call.from_user.id, call.message.chat.id, call.message)


def handle_add_achievement(call: types.CallbackQuery, bot: TeleBot):
    print("HERE")
    al_id = int(call.data.split('_')[-1])
    try:
        ach_list = AchievementList.objects.get(id=al_id)
    except AchievementList.DoesNotExist:
        bot.answer_callback_query(call.id, "Список достижений не найден", show_alert=True)
        return

    bot.set_state(call.from_user.id, HabitStates.achievement_description, call.message.chat.id)
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['ach_list'] = ach_list.id
    bot.send_message(call.message.chat.id, f"{ach_list.name}. Опишите ваше достижение", parse_mode='Markdown')


def handle_add_achievement_description(message: types.Message, bot: TeleBot):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        ach_list = AchievementList.objects.get(id=data['ach_list'])

    ach = Achievement.objects.create(
        user=bot.looser,
        description=message.text,
        achievement_list=ach_list
    )

    bot.delete_state(message.from_user.id, message.chat.id)
    bot.send_message(message.chat.id, achievement_added.format(
        achievement_description=ach.description), parse_mode='Markdown',
                     reply_markup=InlineKeyboardMarkup(
                         [[InlineKeyboardButton("<< Назад к спискам достижений", callback_data="back_al_lists")]]
                     ))


def handle_choice_al(call: types.CallbackQuery, bot: TeleBot):
    al_id = int(call.data.split('_')[-1])
    try:
        ach_list = AchievementList.objects.get(id=al_id)
    except AchievementList.DoesNotExist:
        bot.answer_callback_query(call.id, "Список достижений не найден", show_alert=True)
        return

    AchievementsListActionMenu().mount(bot, call.from_user.id, call.message.chat.id, ach_list,  call.message)


def handle_show_achievement_progress(call: types.CallbackQuery, bot: TeleBot):
    al_id = int(call.data.split('_')[-1])
    try:
        ach_list = AchievementList.objects.get(id=al_id)
    except AchievementList.DoesNotExist:
        bot.answer_callback_query(call.id, "Список достижений не найден", show_alert=True)
        return

    AchievementShowStatMenu().mount(bot, call.from_user.id, call.message.chat.id, ach_list, call.message)


def handle_choose_achievement_period(call: types.CallbackQuery, bot: TeleBot):
    time_interval = None
    if call.data.startswith('week'):
        time_interval = (datetime.now() - timedelta(days=7), datetime.now())
    elif call.data.startswith('month'):
        time_interval = (datetime.now() - timedelta(days=30), datetime.now())

    al_id = int(call.data.split('_')[-1])
    try:
        ach_list = AchievementList.objects.get(id=al_id)
    except AchievementList.DoesNotExist:
        bot.answer_callback_query(call.id, "Список достижений не найден", show_alert=True)
        return

    achievements = ach_list.achievements
    if time_interval is not None:
        achievements = achievements.filter(date__range=time_interval)
    else:
        achievements = achievements.all()

    achievements = list(achievements)

    if not achievements:
        bot.send_message(call.message.chat.id, "За этот период нет достижений", parse_mode='Markdown')
        return

    time_int_dict = {
        'week': 'последнюю неделю',
        'month': 'последний месяц',
        'all_time': 'все время'
    }

    bot.send_message(call.message.chat.id, achievement_stat_template.format(
        achievent_list=ach_list.name,
        time_interval=time_int_dict["_".join(call.data.split('_')[0:-2])],
        achievements="\n".join([f"✅ {ach.description}" for ach in achievements])
    ), parse_mode='Markdown')


def handle_al_delete(call: types.CallbackQuery, bot: TeleBot):
    al_id = int(call.data.split('_')[-1])
    try:
        ach_list = AchievementList.objects.get(id=al_id)
    except AchievementList.DoesNotExist:
        bot.answer_callback_query(call.id, "Список достижений не найден", show_alert=True)
        return

    AchievementListDeleteConfirmMenu().mount(bot, call.from_user.id, call.message.chat.id, ach_list, call.message)


def handle_delete_al_confirm(call: types.CallbackQuery, bot: TeleBot):
    al_id = int(call.data.split('_')[-1])
    try:
        ach_list = AchievementList.objects.get(id=al_id)
    except AchievementList.DoesNotExist:
        bot.answer_callback_query(call.id, "Список достижений не найден", show_alert=True)
        return

    ach_list_name = ach_list.name
    ach_list.delete()
    AchievementListDeletedMenu().mount(bot, call.from_user.id, call.message.chat.id, call.message,
                                       caption=f"Список достижений {ach_list_name} удален")


def handle_retrain(message: types.Message, bot: TeleBot):
    retrain_model()
    bot.send_message(message.chat.id, "Модель переобучена", parse_mode='Markdown')


def handle_recommend_habit(message: types.Message, bot: TeleBot):
    recommend_habit()


