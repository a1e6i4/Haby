from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'
    SUPERUSER = 'superuser'
    ROLE = [
        (USER, 'user'),
        (ADMIN, 'admin'),
        (SUPERUSER, 'superuser'),
    ]
    username = models.CharField(max_length=150, unique=True)
    telegram_id = models.CharField(max_length=30, null=True, blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    password = models.CharField(max_length=150)
    role = models.CharField(max_length=150, choices=ROLE, default=USER)

    def __str__(self):
        return self.username


class Habit(models.Model):
    name = models.CharField(max_length=150)
    unit = models.CharField(max_length=150)
    user = models.ForeignKey(User, related_name='habits', on_delete=models.CASCADE)
    show_template = models.CharField(max_length=400, default='')

    def __str__(self):
        return self.name


class Record(models.Model):
    habit = models.ForeignKey(Habit, related_name='records', on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    value = models.FloatField(default=0)
    cumulative_value = models.FloatField(default=0)

    def __str__(self):
        return f"{self.habit} - {self.date}"


class AchievementList(models.Model):
    name = models.CharField(max_length=150)
    user = models.ForeignKey(User, related_name='achievement_lists', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Achievement(models.Model):
    description = models.TextField()
    user = models.ForeignKey(User, related_name='achievements', on_delete=models.CASCADE)
    achievement_list = models.ForeignKey(AchievementList, related_name='achievements', on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.description[:100]


class Goal(models.Model):
    habit = models.ForeignKey(Habit, related_name='goals', on_delete=models.CASCADE)
    value = models.IntegerField()
    deadline = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.habit} - {self.value} - {self.deadline}"


class Recommender(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    model = models.FileField(upload_to='models/')

    def __str__(self):
        return str(self.timestamp)