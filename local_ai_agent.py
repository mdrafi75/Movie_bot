# local_ai_agent.py - ফাইনাল ফিক্সড ভার্সন

import json
import os
from rapidfuzz import fuzz, process
from datetime import datetime
import re

class LocalAIAgent:
    def __init__(self, cache_manager, user_profile_manager, learning_system):
        self.cache = cache_manager
        self.user_profiles = user_profile_manager
        self.learning = learning_system
        self.cache_file = "data/movies_cache.json"
        
        async def detect_intent(self, message, user_id=None):
            """মেসেজের ইন্টেন্ট ডিটেক্ট করে (ASYNC ভার্সন)"""
            message = message.lower().strip()
            
            # কনফিডেন্স স্কোর কালেকশন
            scores = {
                'greeting': 0.0,
                'help': 0.0,
                'movie_request': 0.0,
                'movie_search': 0.0,
                'conversation': 0.0
            }
            
            # ১. গ্রিটিংস চেক
            greetings = ['হাই', 'হ্যালো', 'হেলো', 'হাই', 'hello', 'hi', 'সালাম', 
                        'ওয়াসা', 'কেমন', 'আছেন', 'আছো']
            greeting_matches = sum(1 for g in greetings if g in message)
            if greeting_matches > 0:
                scores['greeting'] = min(0.8 + (greeting_matches * 0.1), 1.0)
            
            # ২. হেল্প চেক
            help_words = ['সাহায্য', 'help', 'কিভাবে', 'how to', 'instructions', 'কি ভাবে']
            if any(h in message for h in help_words):
                scores['help'] = 0.9
            
            # ৩. রিকোয়েস্ট চেক
            request_words = ['চাই', 'লাগবে', 'দরকার', 'request', 'req', 'আনতে হবে', 'পাব']
            request_matches = sum(1 for r in request_words if r in message)
            if request_matches > 0:
                movie_name = self._extract_movie_name_from_request(message)
                scores['movie_request'] = 0.8 + (request_matches * 0.05)
            
            # ৪. মুভি সার্চ চেক (শব্দ সংখ্যা ও প্যাটার্ন)
            words = message.split()
            if 1 <= len(words) <= 4 and not any(c in message for c in ['?', 'কি', 'কে']):
                scores['movie_search'] = 0.7
            
            # ৫. কনভারসেশন চেক
            if '?' in message or any(q in message for q in ['কি', 'কে', 'কেন', 'কখন']):
                scores['conversation'] = 0.8
            
            # সর্বোচ্চ স্কোর খুঁজুন
            max_intent = max(scores, key=scores.get)
            max_score = scores[max_intent]
            
            # যদি কোনো স্কোর ০.৫ এর নিচে হয়, তাহলে ডিফল্ট
            if max_score < 0.5:
                return {
                    "intent": "unknown",
                    "movie_name": None,
                    "confidence": 0.3
                }
            
            # রেজাল্ট তৈরি
            result = {
                "intent": max_intent,
                "confidence": max_score
            }
            
            if max_intent == 'movie_request':
                result['movie_name'] = self._extract_movie_name_from_request(message)
            elif max_intent == 'movie_search':
                result['movie_name'] = message
            else:
                result['movie_name'] = None
            
            return result
    
    def _extract_movie_name_from_request(self, message):
        """রিকোয়েস্ট থেকে মুভির নাম বের করে"""
        message = re.sub(r'(চাই|লাগবে|দরকার|request|req|আনতে হবে)', '', message)
        return message.strip()
    
    def search_movies(self, query, threshold=50):
        """ফাজি সার্চ করে মুভি খোঁজে - ইমপ্রুভড ভার্সন"""
        all_movies = self.cache.get_all_movies()
        if not all_movies:
            return []
        
        results = []
        query_lower = query.lower().strip()
        query_words = set(query_lower.split())
        
        print(f"\n🔍 Searching for: '{query_lower}'")
        
        for movie in all_movies:
            title = movie.get('title', '').lower()
            if not title:
                continue
            
            # বেস স্কোর
            score = 0
            match_reason = ""
            
            # ১. এক্সাক্ট ম্যাচ (সবচেয়ে বেশি প্রায়োরিটি)
            if query_lower == title:
                score = 100
                match_reason = "exact match"
            
            # ২. ডিজেল স্পেশাল কেস (জনপ্রিয় মুভি)
            elif 'diesel' in title and ('disil' in query_lower or 'diesel' in query_lower):
                score = 95
                match_reason = "diesel special case"
            
            # ৩. কোয়েরি টাইটেলের মধ্যে আছে কিনা
            elif query_lower in title:
                score = 90
                match_reason = "query in title"
            
            # ৪. টাইটেলের প্রথম শব্দ ম্যাচ
            elif title.startswith(query_lower):
                score = 85
                match_reason = "title starts with query"
            
            else:
                # ৫. ফাজি রেশিও
                ratio_score = fuzz.ratio(query_lower, title)
                if ratio_score > 70:
                    score = ratio_score
                    match_reason = f"fuzzy ratio {ratio_score}"
                
                # ৬. পার্শিয়াল রেশিও
                partial_score = fuzz.partial_ratio(query_lower, title)
                if partial_score > score:
                    score = partial_score * 0.9
                    match_reason = f"partial ratio {partial_score}"
                
                # ৭. টোকেন সর্ট রেশিও
                token_sort_score = fuzz.token_sort_ratio(query_lower, title)
                if token_sort_score > score:
                    score = token_sort_score * 0.85
                    match_reason = f"token sort {token_sort_score}"
                
                # ৮. শব্দ ম্যাচিং
                title_words = set(title.split())
                common_words = query_words.intersection(title_words)
                if common_words:
                    word_score = len(common_words) * 20
                    if word_score > score:
                        score = word_score
                        match_reason = f"word match {common_words}"
            
            # Popularity bonus (যে মুভি বেশি সার্চ হয়)
            search_count = self.learning.get_search_count(movie['title'])
            if search_count > 5:
                score += 5
                match_reason += " +popular"
            
            if score >= threshold:
                results.append({
                    "movie": movie,
                    "score": min(score, 100),
                    "match_reason": match_reason
                })
                print(f"   {title[:30]}... → score: {score:.1f} ({match_reason})")
        
        # স্কোর অনুযায়ী সাজানো
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # টপ রেজাল্ট প্রিন্ট
        if results:
            print(f"🏆 Top match: {results[0]['movie']['title']} (score: {results[0]['score']:.1f})")
        else:
            print("❌ No matches found")
        
        return results
    
    def get_similar_movies(self, movie, limit=3):
        """একই রকম মুভি খুঁজে"""
        if not movie:
            return []
        
        all_movies = self.cache.get_all_movies()
        similar = []
        movie_genre = movie.get('genre', '').lower()
        movie_title = movie['title'].lower()
        
        for m in all_movies:
            if m['title'] == movie['title']:
                continue
            
            score = 0
            if movie_genre and m.get('genre', '').lower() == movie_genre:
                score += 50
            
            title_score = fuzz.ratio(movie_title, m['title'].lower())
            score += title_score * 0.3
            
            if score > 30:
                similar.append((score, m))
        
        similar.sort(reverse=True, key=lambda x: x[0])
        return [m for s, m in similar[:limit]]
    
    def get_trending_movies(self, limit=5):
        """ট্রেন্ডিং মুভি খুঁজে"""
        trending_titles = self.learning.get_trending(limit*2)
        if not trending_titles:
            return []
        
        all_movies = self.cache.get_all_movies()
        trending = []
        for title in trending_titles:
            for movie in all_movies:
                if movie['title'].lower() == title.lower():
                    trending.append(movie)
                    break
        
        return trending[:limit]
    
    def get_personalized_recommendations(self, user_id, limit=3):
        """ইউজারের পছন্দ অনুযায়ী রিকমেন্ডেশন"""
        profile = self.user_profiles.get_user_profile(user_id)
        preferred_genres = self.user_profiles.get_preferred_genres(user_id)
        
        if not preferred_genres:
            return self.get_trending_movies(limit)
        
        all_movies = self.cache.get_all_movies()
        scored = []
        
        for movie in all_movies:
            score = 0
            movie_genre = movie.get('genre', '').lower()
            
            if movie_genre in preferred_genres:
                score += 50
            
            search_count = self.learning.get_search_count(movie['title'])
            score += min(search_count, 30)
            
            if score > 20:
                scored.append((score, movie))
        
        scored.sort(reverse=True, key=lambda x: x[0])
        return [m for s, m in scored[:limit]]
    
    def format_response(self, intent, query, matches, user_id=None):
        """JSON রেসপন্স ফরম্যাট করে"""
        response = {
            "intent": intent,
            "movie_name": query,
            "matches": [],
            "recommendations": [],
            "admin_request": False,
            "message": ""
        }
        
        if intent == "greeting":
            response["message"] = "👋 হ্যালো! আমি মুভি খুঁজে দেই। আপনার পছন্দের মুভির নাম লিখুন।"
            
        elif intent == "help":
            response["message"] = "📝 শুধু মুভির নাম লিখুন (যেমন: 'diesel', 'kgf')। অথবা /req কমান্ড দিয়ে রিকোয়েস্ট করুন।"
            
        elif intent == "movie_request":
            response["admin_request"] = True
            response["message"] = f"📨 আপনার '{query}' রিকোয়েস্ট নেওয়া হয়েছে। এডমিন শীঘ্রই দেখবেন।"
            
        elif intent == "movie_search":
            if matches:
                top_match = matches[0]
                score = top_match['score']
                movie = top_match['movie']
                
                match_data = {
                    "title": movie['title'],
                    "score": score,
                    "year": movie.get('year', 'N/A'),
                    "genre": movie.get('genre', 'N/A'),
                    "rating": movie.get('rating', 'N/A'),
                    "poster": movie.get('image_url', ''),
                    "links": {
                        "download": movie.get('detail_link', '')
                    }
                }
                response["matches"].append(match_data)
                
                if score >= 85:
                    response["message"] = f"✅ {movie['title']} পাওয়া গেছে!"
                elif score >= 70:
                    response["message"] = f"🤔 আপনি কি '{movie['title']}' খুঁজছেন?"
                else:
                    response["message"] = f"🎬 আপনার জন্য কিছু সাজেশন:"
                
                similar = self.get_similar_movies(movie)
                for m in similar:
                    response["recommendations"].append({
                        "title": m['title'],
                        "year": m.get('year', 'N/A'),
                        "poster": m.get('image_url', '')
                    })
            else:
                response["admin_request"] = True
                response["message"] = f"❌ '{query}' খুঁজে পাইনি। রিকোয়েস্ট পাঠানো হয়েছে।"
                
                trending = self.get_trending_movies(3)
                for m in trending:
                    response["recommendations"].append({
                        "title": m['title'],
                        "year": m.get('year', 'N/A'),
                        "poster": m.get('image_url', '')
                    })
        
        return response