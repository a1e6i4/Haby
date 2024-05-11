import re
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_show_template(template):
    """
    replace number with {value}
    number can be float or integer, delimeter is dot or comma
    """
    return re.sub(r'(\d+[\.,]?\d*)', '{value}', template)


def format_number(number):
    if number == int(number):
        return int(number)


def create_markup(values, callback_data, width=2, back=None):
    n = len(values)
    result = []
    for i in range(0, n, width):
        result.append([InlineKeyboardButton(values[j], callback_data=callback_data[j], resize_keyboard=True)
                       for j in range(i, min(n, i + width))])

    if back is not None:
        result.append([InlineKeyboardButton("<< Назад", callback_data="back")])
    return InlineKeyboardMarkup(result)
