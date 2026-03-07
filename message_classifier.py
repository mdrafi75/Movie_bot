# message_classifier.py - NEW VERSION (AI-চালিত)
import re
from config import BLACKLISTED_MESSAGES

class MessageClassifier:
    def __init__(self, cache_manager, ai_agent=None):
        self.cache_manager = cache_manager
        self.ai_agent = ai_agent  # AI agent যোগ হয়েছে
        self.blacklist = BLACKLISTED_MESSAGES
    
    async def classify_message(self, text, user_id=None, context=None):
        """
        AI দিয়ে মেসেজ ক্লাসিফাই করবে
        """
        if not text or not text.strip():
            return "UNKNOWN"
        
        # ১. ব্ল্যাকলিস্টেড চেক (দ্রুত)
        if self.is_blacklisted(text):
            return "BLACKLISTED"
        
        # ২. AI দিয়ে ইন্টেন্ট ডিটেক্ট (যদি থাকে)
        if self.ai_agent:
            intent_data = await self.ai_agent.detect_intent(text, context)
            
            if intent_data['intent'] == 'movie_search':
                return "MOVIE_QUERY"
            elif intent_data['intent'] == 'movie_request':
                return "MOVIE_REQUEST"
            elif intent_data['intent'] == 'greeting':
                return "GREETING"
            elif intent_data['intent'] == 'help':
                return "HELP"
        
        # ৩. ফ্যালব্যাক: পুরোনো পদ্ধতি
        if self.is_movie_query(text):
            return "MOVIE_QUERY"
        
        return "UNKNOWN"
    
    def is_blacklisted(self, text):
        """মেসেজটি ব্ল্যাকলিস্টেড কিনা"""
        text_lower = text.lower()
        return any(item.lower() in text_lower for item in self.blacklist)
    
    def is_movie_query(self, text):
        """ফ্যালব্যাক: পুরোনো পদ্ধতি"""
        words = text.split()
        if not (1 <= len(words) <= 4):
            return False
        
        if self.contains_links_or_mentions(text):
            return False
        
        return True
    
    def contains_links_or_mentions(self, text):
        """লিংক বা mention আছে কিনা"""
        link_patterns = [
            r'http[s]?://', r'www\.', r't\.me/', r'telegram\.me/',
            r'@\w+', r'/\w+'
        ]
        
        text_lower = text.lower()
        for pattern in link_patterns:
            if re.search(pattern, text_lower):
                return True
        return False