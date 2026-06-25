import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Smart_Agent.settings")
django.setup()

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from Inbox.models import Conversation, Message

class Command(BaseCommand):
    help = 'Seeds the database with an admin user and initial sample support conversations.'

    def handle(self, *args, **options):
        User = get_user_model()
        email = "admin@test.com"
        password = "admin123"

        self.stdout.write("Seeding database...")


        agent, created = User.objects.get_or_create(
            email=email,
            defaults={'username': email}
        )
        if created:
            agent.set_password(password)
            agent.is_staff = True
            agent.is_superuser = True
            agent.save()
            self.stdout.write(self.style.SUCCESS(f"Created support agent admin account: {email} / {password}"))
        else:
            agent.set_password(password)
            agent.save()
            self.stdout.write(self.style.SUCCESS(f"Support agent admin account already existed. Updated password for: {email}"))

        # 2. Clear old conversation data to start fresh (optional, but good for resetting)
        Conversation.objects.all().delete()

        # 3. Create Sample Conversation John Doe
        customer=Conversation.objects.create(customer_name="John Doe", status="open")
        Message.objects.create(conversation=customer, sender="customer", message="Need help")
        
        # Message.objects.create(conversation=c1, sender="agent")
        self.stdout.write(self.style.SUCCESS("Database seeded"))
