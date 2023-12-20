from django.shortcuts import render
from rest_framework import generics
from .serializers import NewsApiViewsSerializer, TagsApiViewsSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import News_bot, Tags_bot

class NewsApiViews(generics.ListAPIView):
    queryset = News_bot.objects.all()
    serializer_class = NewsApiViewsSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class TagsApiViews(generics.ListAPIView):
    queryset = Tags_bot.objects.all()
    serializer_class = TagsApiViewsSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]