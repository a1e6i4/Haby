from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from telebot import types
from telebot.storage import StateRedisStorage

from bot.telegram.bot import HabitsBot
from django.conf import settings


@csrf_exempt
def process_update(request):
    print('process_update')
    json_string = request.body.decode('utf-8')
    update = types.Update.de_json(json_string)

    with HabitsBot(token=settings.TELEGRAM_TOKEN, state_storage=StateRedisStorage(
        host=settings.REDIS_HOST, port=settings.REDIS_PORT, password=settings.REDIS_PASSWORD
    )) as client:
        client.process_new_updates([update])

    return HttpResponse(status=200)
