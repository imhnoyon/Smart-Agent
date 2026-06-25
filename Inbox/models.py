from django.db import models

class Conversation(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('snoozed', 'Snoozed'),
        ('closed', 'Closed'),
    ]

    SENTIMENT_CHOICES = [
        ('Positive', 'Positive'),
        ('Neutral', 'Neutral'),
        ('Negative', 'Negative'),
    ]

    customer_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='open')
    sentiment = models.CharField(max_length=20,choices=SENTIMENT_CHOICES,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer_name} ({self.status})"


class Message(models.Model):
    SENDER_CHOICES = [
        ('customer', 'Customer'),
        ('agent', 'Agent'),
    ]

    conversation = models.ForeignKey(Conversation,related_name='messages',on_delete=models.CASCADE)
    sender = models.CharField(max_length=20,choices=SENDER_CHOICES)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.message[:30]}"
