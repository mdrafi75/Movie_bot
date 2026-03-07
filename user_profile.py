# user_profile.py
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

class UserProfileManager:
    def __init__(self, profile_file="data/user_profiles.json"):
        self.profile_file = profile_file
        self.profiles = self.load_profiles()
        
    def load_profiles(self):
        """ইউজার প্রোফাইল লোড"""
        os.makedirs(os.path.dirname(self.profile_file), exist_ok=True)
        if os.path.exists(self.profile_file):
            with open(self.profile_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_profiles(self):
        """প্রোফাইল সেভ"""
        with open(self.profile_file, 'w', encoding='utf-8') as f:
            json.dump(self.profiles, f, ensure_ascii=False, indent=2)
    
    def get_user_profile(self, user_id, username=None, first_name=None):
        """ইউজার প্রোফাইল রিটার্ন"""
        user_id = str(user_id)
        if user_id not in self.profiles:
            self.profiles[user_id] = {
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'first_seen': datetime.now().isoformat(),
                'last_active': datetime.now().isoformat(),
                'search_history': [],
                'genre_preferences': defaultdict(int),
                'actor_preferences': defaultdict(int),
                'total_searches': 0,
                'favorite_movies': [],
                'clicked_movies': []
            }
        else:
            # আপডেট
            self.profiles[user_id]['last_active'] = datetime.now().isoformat()
            if username:
                self.profiles[user_id]['username'] = username
            if first_name:
                self.profiles[user_id]['first_name'] = first_name
        
        return self.profiles[user_id]
    
    def update_from_search(self, user_id, movie):
        """সার্চ থেকে প্রোফাইল আপডেট"""
        user_id = str(user_id)
        if user_id not in self.profiles:
            return
        
        profile = self.profiles[user_id]
        
        # সার্চ হিস্টোরি
        profile['search_history'].append({
            'movie_title': movie['title'],
            'timestamp': datetime.now().isoformat()
        })
        profile['total_searches'] += 1
        
        # জেনার প্রেফারেন্স (if available)
        if 'genre' in movie and movie['genre']:
            genre = movie['genre'].lower()
            profile['genre_preferences'][genre] = profile['genre_preferences'].get(genre, 0) + 1
        
        # ফেবারিট মুভি (যে মুভি বারবার খোঁজে)
        movie_title = movie['title']
        if movie_title not in profile['favorite_movies']:
            profile['favorite_movies'].append(movie_title)
        
        # লিমিট ২০
        if len(profile['search_history']) > 20:
            profile['search_history'] = profile['search_history'][-20:]
        if len(profile['favorite_movies']) > 10:
            profile['favorite_movies'] = profile['favorite_movies'][-10:]
        
        self.save_profiles()
    
    def update_from_click(self, user_id, movie_title):
        """ডাউনলোড/ক্লিক ট্র্যাক"""
        user_id = str(user_id)
        if user_id not in self.profiles:
            return
        
        profile = self.profiles[user_id]
        profile['clicked_movies'].append({
            'title': movie_title,
            'timestamp': datetime.now().isoformat()
        })
        
        if len(profile['clicked_movies']) > 20:
            profile['clicked_movies'] = profile['clicked_movies'][-20:]
        
        self.save_profiles()
    
    def get_preferred_genres(self, user_id, limit=3):
        """ইউজারের পছন্দের জেনার"""
        user_id = str(user_id)
        if user_id not in self.profiles:
            return []
        
        prefs = self.profiles[user_id]['genre_preferences']
        sorted_genres = sorted(prefs.items(), key=lambda x: x[1], reverse=True)
        return [g for g, c in sorted_genres[:limit]]