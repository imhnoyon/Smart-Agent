import time
from django.core.cache import cache

def get_lock_key(conversation_id):
    return f"lock:conversation:{conversation_id}"

def get_lock_state(conversation_id):
    key = get_lock_key(conversation_id)
    lock_data = cache.get(key)
    
    if not lock_data:
        return {'locked': False}
        
    now = time.time()
    expires_at = lock_data.get('expires_at', 0)
    expires_in_seconds = int(expires_at - now)
    
    if expires_in_seconds <= 0:
        cache.delete(key)
        return {'locked': False}
        
    return {
        'locked': True,
        'owner_id': lock_data['owner_id'],
        'owner_username': lock_data['owner_username'],
        'expires_in_seconds': expires_in_seconds,
        'acquired_at': lock_data['acquired_at']
    }

def acquire_lock(conversation_id, user):
    key = get_lock_key(conversation_id)
    lock_state = get_lock_state(conversation_id)
    
    if lock_state['locked']:
        if lock_state['owner_id'] != user.id:
            return False, lock_state
        
    now = time.time()
    ttl = 300 
    lock_data = {
        'owner_id': user.id,
        'owner_username': user.username,
        'acquired_at': now,
        'expires_at': now + ttl
    }
    
    cache.set(key, lock_data, timeout=ttl)
    
    return True, {
        'locked': True,
        'owner_id': user.id,
        'owner_username': user.username,
        'expires_in_seconds': ttl,
        'acquired_at': now
    }

def release_lock(conversation_id, user):
    key = get_lock_key(conversation_id)
    lock_state = get_lock_state(conversation_id)
    
    if not lock_state['locked']:
        return True, "No active lock found."
        
    if lock_state['owner_id'] != user.id:
        return False, "You do not own this lock."
        
    cache.delete(key)
    return True, "Lock released successfully."
