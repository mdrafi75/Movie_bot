# message_classifier.py - নতুন ফাইল তৈরি করুন
import re
from config import BLACKLISTED_MESSAGES, MOVIE_PATTERNS

class MessageClassifier:
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
        self.blacklist = BLACKLISTED_MESSAGES
    
    def classify_message(self, text):
        if not text or not text.strip():
            return "UNKNOWN"
            
        text = text.strip()
        
        # ১. প্রথমে ব্ল্যাকলিস্টেড চেক
        if self.is_blacklisted(text):
            return "BLACKLISTED"
        
        # ২. মুভি কোয়েরি চেক
        if self.is_movie_query(text):
            return "MOVIE_QUERY"
        
        return "UNKNOWN" 
    
    def is_blacklisted(self, text):
        """মেসেজটি ব্ল্যাকলিস্টেড কিনা চেক করবে"""
        text_lower = text.lower()
        return any(item.lower() in text_lower for item in self.blacklist)
    
    def is_movie_query(self, text):
        """মেসেজটি মুভি কোয়েরি কিনা চেক করবে"""
        # শব্দ সংখ্যা চেক (1-4 words)
        words = text.split()
        if not (1 <= len(words) <= 4):
            return False
        
        # লিংক বা mention চেক
        if self.contains_links_or_mentions(text):
            return False
        
        # মুভি প্যাটার্ন ম্যাচ
        for pattern in MOVIE_PATTERNS:
            if re.match(pattern, text, re.IGNORECASE):
                return True
        
        # ক্যাশে থেকে পার্শিয়াল ম্যাচ চেক
        return self.has_partial_match_in_cache(text)
    
    def contains_links_or_mentions(self, text):
        """লিংক বা mention আছে কিনা চেক করবে"""
        link_patterns = [
            r'http[s]?://', r'www\.', r't\.me/', r'telegram\.me/',
            r'[\w]+\.[a-z]{2,}', r'bit\.ly/', r'goo\.gl/', 
            r'@\w+', r'/\w+'  # mentions and commands
        ]
        
        text_lower = text.lower()
        for pattern in link_patterns:
            if re.search(pattern, text_lower):
                return True
        return False
    
    def has_partial_match_in_cache(self, query):
        """ক্যাশে থেকে পার্শিয়াল ম্যাচ চেক করবে"""
        try:
            movies = self.cache_manager.get_all_movies()
            query_lower = query.lower()
            
            for movie in movies:
                title_lower = movie['title'].lower()
                # পার্শিয়াল ম্যাচ চেক
                if query_lower in title_lower or title_lower in query_lower:
                    return True
                    
                # শব্দ ভিত্তিতে ম্যাচ
                query_words = set(query_lower.split())
                title_words = set(title_lower.split())
                if query_words.intersection(title_words):
                    return True
                    
            return False
        except:
            return False

# টেস্ট করার জন্য
if __name__ == "__main__":
    # ডেমো টেস্ট
    from cache_manager import CacheManager
    cache = CacheManager()
    classifier = MessageClassifier(cache)
    
    test_messages = [
        "kgf",
        "হ্যালো ভাই", 
        "inception",
        "https://t.me/test",
        "বাহুবলী",
        "কেমন আছো",
        "avngr"
    ]
    
    for msg in test_messages:
        result = classifier.classify_message(msg)
        print(f"'{msg}' -> {result}")