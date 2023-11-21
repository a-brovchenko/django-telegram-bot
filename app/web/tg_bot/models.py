from django.db import models
from django.contrib.auth.models import AbstractUser


class News(models.Model):
    news = models.CharField(max_length=400)
    site = models.CharField(max_length=200)
    tags = models.CharField(max_length=100)
    data_publisher = models.DateTimeField()
    add_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.tags
    

class User(AbstractUser):
    telegram_id = models.IntegerField(default=0, unique=True)
    token = models.CharField(max_length=50)

    def __str__(self):
        return str(self.telegram_id)
    

class Tags(models.Model):
    telegram_id = models.ForeignKey(User, on_delete=models.CASCADE, to_field='telegram_id')
    tags = models.CharField(max_length=50)

    def __str__(self):
        return str(self.telegram_id)
