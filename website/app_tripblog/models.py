from django.db import models

# Create your models here.

class User(models.Model):
    user_name = models.CharField(max_length=20)
    password = models.CharField(max_length=20)

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