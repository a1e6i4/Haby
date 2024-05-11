from telebot import types, BaseMiddleware
from habits.models import User


class AuthMiddleware(BaseMiddleware):
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot = bot
        self.update_types = ['message', 'callback_query', 'poll_answer']

    def pre_process(self, message, data):
        if isinstance(message, types.PollAnswer):
            user_telegram_id = message.user.id
        else:
            user_telegram_id = message.from_user.id
        try:
            user = User.objects.get(telegram_id=user_telegram_id)
        except User.DoesNotExist:
            user = User.objects.create(
                telegram_id=user_telegram_id,
                username=message.from_user.username or str(user_telegram_id),
                first_name=message.from_user.first_name or str(user_telegram_id),
                last_name=message.from_user.last_name or str(user_telegram_id),
            )

        self.bot.looser = user
        print("User", user.telegram_id)

    def post_process(self, message, data, exception):
        pass
