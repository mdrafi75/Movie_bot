# message_classifier.py - আপডেটেড ভার্সন (কনফিডেন্স স্কোর সহ)
import re
from config import BLACKLISTED_MESSAGES, GREETINGS_KEYWORDS

class MessageClassifier:
    def __init__(self, cache_manager, ai_agent=None):
        self.cache_manager = cache_manager
        self.ai_agent = ai_agent
        self.blacklist = BLACKLISTED_MESSAGES
        self.greetings = GREETINGS_KEYWORDS  

        # ডিবাগ প্রিন্ট যোগ করুন (নতুন)
        if self.ai_agent:
            print(f"✅ AI Agent loaded: {type(self.ai_agent).__name__}")
        else:
            print("⚠️ No AI Agent provided")
        
        # কনভারসেশনাল প্যাটার্ন
        self.greeting_patterns = [
            r'^(হাই|হ্যালো|হেলো|সালাম|নমস্কার|hi|hello|hey|hlw)$',
            r'^(কেমন আছ|কি খবর|how are you|whats up)$',
            r'^(good morning|good afternoon|good evening|শুভ (সকাল|দুপুর|বিকাল|রাত্রি))$',
            r'^(আসসালামু আলাইকুম|ওয়াসালাম)$'
        ]
        
        self.question_patterns = [
            r'.*\?$',
            r'^(কে|কি|কেন|কখন|কোথায়|কিভাবে|কী|কেমনে|what|why|when|where|how)',
            r'^(আছে কি|পাব কি|দিবেন কি|can you|will you|do you)'
        ]
        
        self.thanks_patterns = [
            r'^(ধন্যবাদ|থ্যাংকস|thanks|thank you|ওয়েলকাম|welcome)$'
        ]
        
        # মুভি প্যাটার্ন
        self.movie_patterns = [
            r'^[a-zA-Z0-9\s]{2,30}$',  # ইংরেজি নাম
            r'^[\u0980-\u09FF\s]{2,20}$',  # বাংলা নাম
            r'.*\b(19|20)\d{2}\b',  # বছর আছে
            r'.*\b(part|chapter|season|episode|ভাগ|পর্ব|সিজন)\b',  # সিরিজ/পার্ট
        ]
    
    async def classify(self, text, user_id=None, chat_type='private'):
        """
        মেসেজ ক্লাসিফাই করে ইন্টেন্ট ও কনফিডেন্স রিটার্ন করবে
        রিটার্ন: {'intent': str, 'confidence': float, 'reason': str}
        """
        if not text or not text.strip():
            return {'intent': 'UNKNOWN', 'confidence': 0.0, 'reason': 'empty_message'}
        
        text_lower = text.lower().strip()
        
        # ১. কমান্ড চেক
        if text.startswith('/'):
            return {'intent': 'COMMAND', 'confidence': 1.0, 'reason': 'starts_with_slash'}
        
        # ২. ব্ল্যাকলিস্ট চেক
        if self.is_blacklisted(text):
            return {'intent': 'BLACKLISTED', 'confidence': 1.0, 'reason': 'blacklisted'}
        
        # ৩. লিংক চেক
        if self.contains_links_or_mentions(text):
            return {'intent': 'SPAM', 'confidence': 0.95, 'reason': 'contains_links'}
        
        # ৪. কনভারসেশনাল প্যাটার্ন চেক
        conv_result = self._check_conversational(text_lower)
        if conv_result['is_conversation']:
            return conv_result
        
        # ৫. AI এজেন্ট দিয়ে চেক (যদি থাকে)
        if self.ai_agent:
            try:
                intent_data = await self.ai_agent.detect_intent(text, user_id)
                if intent_data and intent_data.get('confidence', 0) > 0.6:
                    return {
                        'intent': intent_data['intent'].upper(),
                        'confidence': intent_data['confidence'],
                        'reason': 'ai_detection',
                        'movie_name': intent_data.get('movie_name')
                    }
            except Exception as e:
                print(f"AI detect error: {e}")
        
        # ৬. মুভি কোয়েরি চেক
        movie_result = self._check_movie_query(text)
        if movie_result['is_movie']:
            return {
                'intent': 'MOVIE_QUERY',
                'confidence': movie_result['confidence'],
                'reason': 'movie_pattern',
                'movie_name': text
            }
        
        # ৭. প্রাইভেট চ্যাটে ডিফল্ট MOVIE_QUERY
        if chat_type == 'private':
            return {
                'intent': 'MOVIE_QUERY',
                'confidence': 0.7,
                'reason': 'private_chat_default',
                'movie_name': text
            }
        
        # ৮. গ্রুপে ডিফল্ট UNKNOWN (কম কনফিডেন্সে চুপ থাকবে)
        return {'intent': 'UNKNOWN', 'confidence': 0.3, 'reason': 'no_match'}
    
    def _check_conversational(self, text_lower):
        """কনভারসেশনাল প্যাটার্ন চেক করে"""
        
        # প্রথমে এক্সাক্ট ম্যাচ চেক করুন (পুরো মেসেজ)
        if text_lower in self.greetings:
            return {
                'is_conversation': True,
                'intent': 'GREETING',
                'confidence': 0.98,
                'reason': 'exact_greeting_match'
            }
        
        # তারপর শব্দ ভিত্তিতে চেক (কম কনফিডেন্স)
        words = text_lower.split()
        for word in words:
            if word in self.greetings and len(word) > 1:
                return {
                    'is_conversation': True,
                    'intent': 'GREETING',
                    'confidence': 0.85,
                    'reason': 'greeting_word_match'
                }
        
        # গ্রিটিংস প্যাটার্ন চেক
        for pattern in self.greeting_patterns:
            if re.match(pattern, text_lower, re.IGNORECASE):
                return {
                    'is_conversation': True,
                    'intent': 'GREETING',
                    'confidence': 0.95,
                    'reason': 'greeting_pattern'
                }
        
        # প্রশ্ন চেক
        for pattern in self.question_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return {
                    'is_conversation': True,
                    'intent': 'QUESTION',
                    'confidence': 0.9,
                    'reason': 'question_pattern'
                }
        
        # ধন্যবাদ চেক
        for pattern in self.thanks_patterns:
            if re.match(pattern, text_lower, re.IGNORECASE):
                return {
                    'is_conversation': True,
                    'intent': 'THANKS',
                    'confidence': 0.95,
                    'reason': 'thanks_pattern'
                }
        
        return {'is_conversation': False}
    
    def _check_movie_query(self, text):
        """মুভি কোয়েরি চেক করে"""
        words = text.split()
        
        # খুব বড় মেসেজ (১৫+ শব্দ) - মুভি না
        if len(words) > 8:
            return {'is_movie': False, 'confidence': 0.0}
        
        # খুব ছোট (১ অক্ষর)
        if len(text) < 2:
            return {'is_movie': False, 'confidence': 0.0}
        
        # মুভি প্যাটার্ন চেক
        for pattern in self.movie_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                # দৈর্ঘ্য অনুযায়ী কনফিডেন্স
                if 2 <= len(words) <= 4:
                    confidence = 0.9
                else:
                    confidence = 0.7
                return {'is_movie': True, 'confidence': confidence}
        
        # ক্যাশে চেক (যদি ম্যানেজার থাকে)
        if self.cache_manager:
            movies = self.cache_manager.get_all_movies()
            for movie in movies[:50]:  # প্রথম ৫০টি চেক
                if text.lower() in movie.get('title', '').lower():
                    return {'is_movie': True, 'confidence': 0.8}
        
        return {'is_movie': False, 'confidence': 0.0}
    
    def is_blacklisted(self, text):
        """মেসেজটি ব্ল্যাকলিস্টেড কিনা"""
        text_lower = text.lower()
        return any(item.lower() in text_lower for item in self.blacklist)
    
    def contains_links_or_mentions(self, text):
        """লিংক বা mention আছে কিনা"""
        link_patterns = [
            r'http[s]?://', r'www\.', r't\.me/', r'telegram\.me/',
            r'@\w+', r'/\w+', r'bit\.ly', r'tinyurl', r'goo\.gl'
        ]
        
        text_lower = text.lower()
        for pattern in link_patterns:
            if re.search(pattern, text_lower):
                return True
        return False