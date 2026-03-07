# context_memory.py
from collections import defaultdict, deque
from datetime import datetime

class ContextMemory:
    def __init__(self, max_history=5):
        self.max_history = max_history
        self.user_context = defaultdict(lambda: deque(maxlen=max_history))
        self.conversation_state = defaultdict(dict)
    
    def add_message(self, user_id, message, response=None):
        """ইউজারের মেসেজ মেমোরিতে যোগ"""
        user_id = str(user_id)
        self.user_context[user_id].append({
            'message': message,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_context(self, user_id):
        """ইউজারের কনটেক্সট রিটার্ন"""
        user_id = str(user_id)
        return list(self.user_context.get(user_id, []))
    
    def get_last_message(self, user_id):
        """শেষ মেসেজ"""
        user_id = str(user_id)
        context = self.user_context.get(user_id, [])
        return context[-1] if context else None
    
    def set_state(self, user_id, key, value):
        """কনভারসেশন স্টেট সেট"""
        user_id = str(user_id)
        self.conversation_state[user_id][key] = value
    
    def get_state(self, user_id, key, default=None):
        """কনভারসেশন স্টেট গেট"""
        user_id = str(user_id)
        return self.conversation_state[user_id].get(key, default)
    
    def clear_state(self, user_id):
        """স্টেট ক্লিয়ার"""
        user_id = str(user_id)
        self.conversation_state[user_id] = {}