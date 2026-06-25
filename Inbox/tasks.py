from celery import shared_task
from django.db import transaction
from .models import Conversation
from .services.sentiment_analyzer import sentiment_analyzer

@shared_task
def analyze_conversation_sentiment_task(conversation_id):
    try:
        with transaction.atomic():
            conversation = Conversation.objects.select_for_update().get(id=conversation_id)
            messages = conversation.messages.all().order_by('timestamp')
            
            if not messages.exists():
                conversation.sentiment = 'Neutral'
                conversation.save()
                return 'Neutral'
            combined_text = " ".join([m.message for m in messages])
            sentiment = sentiment_analyzer.analyze(combined_text)
            conversation.sentiment = sentiment
            conversation.save()
            
            return sentiment
    except Conversation.DoesNotExist:
        return None
