
from django.contrib import admin
from django.urls import path
from tg_bot.views import NewsApiViews, TagsApiViews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/news/', NewsApiViews.as_view()),
    path('api/tags/', TagsApiViews.as_view()),
]
