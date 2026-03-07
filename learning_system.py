# learning_system.py
import json
import os
from datetime import datetime, timedelta
from collections import Counter

class LearningSystem:
    def __init__(self, cache_file="data/learning_cache.json"):
        self.cache_file = cache_file
        self.data = self.load_data()
        
    def load_data(self):
        """লার্নিং ডাটা লোড"""
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'spelling_patterns': {},  # ভুল বানান → সঠিক নাম
            'search_counts': {},       # মুভি সার্চ কাউন্ট
            'trending_cache': {},       # ট্রেন্ডিং ক্যাশ
            'common_queries': [],       # কমন কোয়েরি
            'last_updated': None
        }
    
    def save_data(self):
        """ডাটা সেভ"""
        self.data['last_updated'] = datetime.now().isoformat()
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def learn_spelling(self, wrong_query, correct_title):
        """বানান ভুল শেখে"""
        key = wrong_query.lower().strip()
        self.data['spelling_patterns'][key] = correct_title
        
        # লিমিট ৫০০
        if len(self.data['spelling_patterns']) > 500:
            # পুরোনো ডাটা রিমুভ
            keys = list(self.data['spelling_patterns'].keys())[-500:]
            self.data['spelling_patterns'] = {k: self.data['spelling_patterns'][k] for k in keys}
        
        self.save_data()
    
    def get_corrected_name(self, query):
        """শেখা প্যাটার্ন থেকে সঠিক নাম"""
        return self.data['spelling_patterns'].get(query.lower().strip())
    
    def track_search(self, movie_title):
        """সার্চ ট্র্যাক করে"""
        title = movie_title.lower().strip()
        self.data['search_counts'][title] = self.data['search_counts'].get(title, 0) + 1
        
        # ট্রেন্ডিং আপডেট
        self.update_trending()
        self.save_data()
    
    def update_trending(self):
        """ট্রেন্ডিং মুভি আপডেট"""
        # সর্ট করে টপ ২০
        sorted_counts = sorted(
            self.data['search_counts'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        self.data['trending_cache'] = {
            'movies': [m for m, c in sorted_counts[:10]],
            'updated': datetime.now().isoformat()
        }
    
    def get_trending(self, limit=5):
        """ট্রেন্ডিং মুভি রিটার্ন"""
        if 'trending_cache' in self.data:
            return self.data['trending_cache'].get('movies', [])[:limit]
        return []
    
    def get_search_count(self, movie_title):
        """মুভির সার্চ কাউন্ট"""
        return self.data['search_counts'].get(movie_title.lower().strip(), 0)
    
    def get_pattern_confidence(self, wrong_query):
        """কতবার এই প্যাটার্ন শিখেছে সেটা রিটার্ন করে"""
        # এই ফাংশনটা learning_system.py-তে যোগ করো
        # সিম্পল ভার্সন:
        return 1  # ১ বার শিখেছে