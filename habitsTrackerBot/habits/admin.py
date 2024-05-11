from django.contrib import admin
from .models import User, Habit, Record, Goal, Achievement, AchievementList, Recommender

admin.site.register(User)
admin.site.register(Habit)
admin.site.register(Record)
admin.site.register(Goal)
admin.site.register(Achievement)
admin.site.register(AchievementList)
admin.site.register(Recommender)
