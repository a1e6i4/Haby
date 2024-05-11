import logging
from django.utils import timezone
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from openai import OpenAI
from telebot import TeleBot

from habits.models import User, Habit, Recommender
import numpy as np
from implicit.als import AlternatingLeastSquares
from scipy.sparse import csr_matrix
import pickle
from django.core import files


@shared_task
def strikes_notify():
    yesterday = timezone.now() - timedelta(days=1)
    for user in User.objects.all():
        records = user.records.order_by('-date').filter(date__lte=yesterday)
        strike = 1
        last_day = yesterday
        for record in records:
            # check if record date is not far then 1 day from last_day
            if last_day - record.date <= timedelta(days=1):
                strike += 1
                last_day = record.date
            else:
                break

        TeleBot(token=settings.TELEGRAM_TOKEN).send_message(user.telegram_id, f"Ты отмечаешь привычки {strike} дней подряд, так держать!")


@shared_task
def retrain_model():
    habits = Habit.objects.all()
    users = User.objects.all()
    habit_names = list({habit.name.lower() for habit in habits})

    user_ids = {user.id: i for i, user in enumerate(users)}
    habit_ids = {habit_name: i for i, habit_name in enumerate(habit_names)}
    rows, cols, vals = [], [], []
    for habit in habits:
        rows.append(user_ids[habit.user.id])
        cols.append(habit_ids[habit.name.lower()])
        vals.append(1)

    interaction_matrix = csr_matrix((vals, (rows, cols)), shape=(len(users), len(habit_names)))

    model = AlternatingLeastSquares(factors=50, iterations=30)
    model.fit(interaction_matrix)




    # save model as pkl file field in Recommender model
    # create new recommender
    recommender = Recommender.objects.create()
    with open(f"model_{recommender.id}.pkl", 'wb') as f:
        pickle.dump({
            'model': model,
            'user_ids': user_ids,
            'habit_ids': habit_ids,
            'matrix': interaction_matrix,
        }, f)

    with open(f"model_{recommender.id}.pkl", 'rb') as f:
        recommender.model.save(f"model_{recommender.id}.pkl", files.File(f))
        recommender.save()


@shared_task
def recommend_habit():
    users = User.objects.all()

    recommender = Recommender.objects.last()

    with open('model.pkl', 'wb') as f:
        f.write(recommender.model.read())

    with open('model.pkl', 'rb') as f:
        model_dct = pickle.load(f)

    model = model_dct['model']
    user_ids = model_dct['user_ids']
    habit_ids = model_dct['habit_ids']
    matrix = model_dct['matrix']

    for user in users:
        try:
            user_id = user.id

            ids, scores = model.recommend(user_ids[user_id], matrix[user_ids[user_id]])
            habit_idx = ids[np.argmax(scores)]
            habit_id = habit_ids.get(habit_idx)

            try:
                habit = Habit.objects.get(id=habit_id)
            except Habit.DoesNotExist:
                # random habit
                habit = Habit.objects.exclude(user_id=user_id).order_by('?').first()

            user = User.objects.get(id=user_id)
            TeleBot(token=settings.TELEGRAM_TOKEN).send_message(user.telegram_id,
                                                                f"Попробуйте завести привычку \"{habit.name}\"!",
                                                                parse_mode='Markdown')
        except Exception as e:
            logging.error(f"Error while recommending habit for user {user_id}: {e}")
            continue
