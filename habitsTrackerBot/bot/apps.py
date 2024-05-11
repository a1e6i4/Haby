from django.apps import AppConfig
from django.conf import settings
from telebot import TeleBot


class BotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bot'

    def ready(self):
        webhook_url = f"{settings.TELEGRAM_WEBHOOK_HOST}bot/process"
        TeleBot(settings.TELEGRAM_TOKEN).set_webhook(url=webhook_url)
