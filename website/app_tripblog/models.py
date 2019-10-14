from django.db import models
from django_mysql.models import JSONField
# Create your models here.

class User(models.Model):
    user_name = models.CharField(max_length=20)
    user_account = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=20)
    def __str__(self):
        return self.user_account

class UserArticles(models.Model):
    user_account = models.ForeignKey(User, on_delete=models.CASCADE)
    cover_picture = models.CharField(max_length=20, blank=True)
    article_title = models.CharField(max_length=40)
    article_content = JSONField(blank=True)
    def __str__(self):
        return f'{self.user_account.user_account}: {self.article_title}'

class Dog(models.Model):
    name = models.CharField(max_length=200)
    data = JSONField()

class ChatbotCategory(models.Model):
    chatbot_category = models.CharField(max_length=40, unique=True)
    def __str__(self):
        return self.chatbot_category
    
class ChatbotCategory_ch(models.Model):
    chatbot_category = models.CharField(max_length=40, unique=True)
    def __str__(self):
        return self.chatbot_category

class ChatbotQA(models.Model):
    chatbot_category =  models.ForeignKey(ChatbotCategory, on_delete=models.CASCADE)
    chatbot_question = models.CharField(max_length=255)
    chatbot_answer = models.CharField(max_length=255)
    
class ChatbotQA_ch(models.Model):
    chatbot_category =  models.ForeignKey(ChatbotCategory_ch, on_delete=models.CASCADE)
    chatbot_question = models.CharField(max_length=255)
    chatbot_answer = models.CharField(max_length=255)