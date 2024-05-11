goal_complete = """Цель создана: "{goal_value} {habit_unit} к {goal_deadline}"
Чтоб успеть к сроку вам надо {habit_name} {work_per_day} {habit_unit} в день"""


habit_value_added = """🌟 Запись добавлена:

{habit_show_template}
"""


main_menu_template = """Выберите привычки или списки.

📊 Привычки - это то, что можно просуммировать, например, количество прочитанных страниц за месяц.

🏆 Достижения - это различные дела, например: сходить в музей, прочитать книгу... такие дела можно объединять тематически, в списки
"""


habit_show_template = """Как отображать ваши достижения? Напишите шаблон, например:

"Я прочитала 50 страниц, Ура!"
или
"Изучено 100 иностранных слов"

"""

habit_unit_template = """Как измерять прогресс? Напишите единицу измерения, например: литры, страницы, километры, штуки... 📏
"""

habit_stat_period_choice_template = """Выберите период для привычки «{}»"""

habit_stat_template = """За {time_interval} {habit_show_template}"""

habit_action_template = "Выберите действие с привычкой «{}»"

achievement_list_added = """🎖️📝 Список достижений добавлен:

{achievement_list_description}
"""

achievement_added = """🏆 Достижение добавлено:

{achievement_description}
"""

ach_list_action_template = "Выберите действие со списком достижений «{}»"

ach_stat_period_choice_template = """ За какой период вы хотите посмотреть достихения? («{}»)"""


achievement_stat_template = """{achievent_list}: Достижения за {time_interval}

{achievements}
"""