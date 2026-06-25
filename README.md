# Smart Agent Support System

Real-time customer support inbox with Django and WebSockets.

## Setup

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_db
python manage.py collectstatic --noinput
daphne -b 0.0.0.0 -p 8001 Smart_Agent.asgi:application
```

Default admin: `mahedi` / `123`

Server: http://127.0.0.1:8001

## API Endpoints

### Auth
```
POST /api/token/
{
  "email": "admin@test.com",
  "password": "admin123"
}
```

### Conversations (No auth)
```
GET /api/inbox/conversations/?page=1&status=open&search=John
```

### Messages (No auth)
```
GET /api/inbox/conversations/1/messages/

POST /api/inbox/conversations/1/messages/
{
  "sender": "customer",
  "message": "Hello"
}
```

### AI Suggestions (Auth required)
```
POST /api/inbox/conversations/1/suggest-reply/
Authorization: Bearer <token>

{
  "message": "I want to return my order"
}
```

### Locks (Auth required)
```
GET /api/inbox/conversations/1/lock/
POST /api/inbox/conversations/1/lock/acquire/
POST /api/inbox/conversations/1/lock/release/
```

## WebSocket

Connect: `ws://127.0.0.1:8001/ws/conversations/1/?token=<token>`

Send:
```json
{"sender": "agent", "message": "How can i help you?"}
```

Receive:
```json
{
  "event": "message_created",
  "message": {
    "id": 10,
    "sender": "customer",
    "message": "I need to refund...",
    "timestamp": "2026-06-25T10:35:00Z"
  }
}
```

## Tech

Django 6, Channels, Daphne, DRF, JWT, Celery, PostgreSQL
