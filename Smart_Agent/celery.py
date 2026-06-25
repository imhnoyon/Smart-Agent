import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smart_Agent.settings')
app = Celery('Smart_Agent')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
