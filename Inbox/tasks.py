from celery import shared_task
from django.db import transaction
from .models import Conversation
from .services.sentiment_analyzer import sentiment_analyzer

@shared_task
def analyze_conversation_sentiment_task(conversation_id):
    """
    Celery background task that runs sentiment analysis on the conversation
    by aggregating its messages and saving the result back to the database.
    """
    try:
        # Use select_for_update to avoid concurrency issues when saving back to the DB
        with transaction.atomic():
            conversation = Conversation.objects.select_for_update().get(id=conversation_id)
            messages = conversation.messages.all().order_by('timestamp')
            
            if not messages.exists():
                conversation.sentiment = 'Neutral'
                conversation.save()
                return 'Neutral'
                
            # Aggregate message texts
            combined_text = " ".join([m.message for m in messages])
            
            # Analyze sentiment
            sentiment = sentiment_analyzer.analyze(combined_text)
            
            # Update and save the conversation profile
            conversation.sentiment = sentiment
            conversation.save()
            
            return sentiment
    except Conversation.DoesNotExist:
        # Conversation could have been deleted in the meantime
        return None
