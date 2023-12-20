from rest_framework import serializers
from .models import News_bot, Tags_bot

class NewsApiViewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News_bot
        fields = ('news', 'site')


class TagsApiViewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags_bot
        fields = ('tags', )