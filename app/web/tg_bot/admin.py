from django.contrib import admin
from .models import News, User, Tags
from django.contrib.auth.admin import UserAdmin



class NewsAdmin(admin.ModelAdmin):
    list_display = ('news', 'site', 'tags', 'data_publisher', 'add_date')

class UserAdmin(UserAdmin):
    list_display = ('telegram_id', 'token', )


admin.site.register(News, NewsAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Tags)