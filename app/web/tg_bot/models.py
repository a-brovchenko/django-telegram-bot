from django.db import models
from django.contrib.auth.models import AbstractUser
import pytz


class News_bot(models.Model):
    news = models.CharField(max_length=400)
    site = models.CharField(max_length=200)
    tags = models.CharField(max_length=100)
    data_publisher = models.DateTimeField()
    add_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.data_publisher.tzinfo:
            self.data_publisher = pytz.utc.localize(self.data_publisher)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.tags
    

class Users_bot(AbstractUser):
    telegram_id = models.IntegerField(null=True, unique=True)
    token = models.CharField(max_length=50, default=False)

    def __str__(self):
        return str(self.telegram_id)
    

class Tags_bot(models.Model):
    telegram_id = models.ForeignKey(Users_bot, on_delete=models.CASCADE, to_field='telegram_id')
    tags = models.CharField(max_length=50)

    def __str__(self):
        return str(self.telegram_id)
