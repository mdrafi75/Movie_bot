# recommendation_engine.py
from rapidfuzz import fuzz
from collections import Counter

class RecommendationEngine:
    def __init__(self, cache_manager, user_profile_manager, learning_system):
        self.cache = cache_manager
        self.user_profiles = user_profile_manager
        self.learning = learning_system
    
    def get_similar_movies(self, movie, limit=3):
        """একই রকম মুভি খুঁজে"""
        if not movie:
            return []
        
        all_movies = self.cache.get_all_movies()
        similar = []
        
        # মুভির জেনার (if available)
        movie_genre = movie.get('genre', '').lower()
        movie_title = movie['title'].lower()
        
        for m in all_movies:
            if m['title'] == movie['title']:
                continue
            
            score = 0
            
            # জেনার ম্যাচ
            if movie_genre and m.get('genre', '').lower() == movie_genre:
                score += 50
            
            # টাইটেল সিমিলারিটি
            title_score = fuzz.ratio(movie_title, m['title'].lower())
            score += title_score * 0.3
            
            # বছর ম্যাচ
            if m.get('year') == movie.get('year'):
                score += 10
            
            if score > 30:
                similar.append((score, m))
        
        similar.sort(reverse=True, key=lambda x: x[0])
        return [m for s, m in similar[:limit]]
    
    def get_personalized_recommendations(self, user_id, limit=3):
        """ইউজারের পছন্দ অনুযায়ী রিকমেন্ডেশন"""
        profile = self.user_profiles.get_user_profile(user_id)
        preferred_genres = self.user_profiles.get_preferred_genres(user_id)
        
        if not preferred_genres:
            return self.get_trending_recommendations(limit)
        
        all_movies = self.cache.get_all_movies()
        scored_movies = []
        
        for movie in all_movies:
            score = 0
            movie_genre = movie.get('genre', '').lower()
            
            # জেনার ম্যাচ
            if movie_genre in preferred_genres:
                score += 50
            
            # সার্চ কাউন্ট (জনপ্রিয়তা)
            search_count = self.learning.get_search_count(movie['title'])
            score += min(search_count, 30)
            
            if score > 20:
                scored_movies.append((score, movie))
        
        scored_movies.sort(reverse=True, key=lambda x: x[0])
        return [m for s, m in scored_movies[:limit]]
    
    def get_trending_recommendations(self, limit=3):
        """ট্রেন্ডিং মুভি"""
        trending_titles = self.learning.get_trending(limit*2)
        
        if not trending_titles:
            return []
        
        all_movies = self.cache.get_all_movies()
        trending_movies = []
        
        for title in trending_titles:
            for movie in all_movies:
                if movie['title'].lower() == title.lower():
                    trending_movies.append(movie)
                    break
        
        return trending_movies[:limit]
    
    def get_new_releases(self, days=7, limit=3):
        """নতুন রিলিজ"""
        # এই ফিচার ব্লগার API থেকে ইমপ্লিমেন্ট করতে হবে
        # বর্তমানে শুধু প্লেসহোল্ডার
        return []