from django.contrib import admin
from .models import News_bot, Users_bot, Tags_bot
from django.contrib.auth.admin import UserAdmin


@admin.register(News_bot)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('news', 'site', 'tags', 'data_publisher', 'add_date')

@admin.register(Users_bot)
class UserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'token')

@admin.register(Tags_bot)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'tags')
