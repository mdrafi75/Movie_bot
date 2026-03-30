# cache_manager.py - ক্যাশিং সিস্টেম
import json
import os
from datetime import datetime, timedelta

class CacheManager:
    def __init__(self, cache_file="data/movies_cache.json"):
        self.cache_file = cache_file
        self.cache_data = self.load_cache()  # এই লাইনটি নিশ্চিত করুন
    
    def load_cache(self):
        """ক্যাশ ডাটা লোড করবে"""
        try:
            # ডাটা ফোল্ডার তৈরি যদি না থাকে
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            
            # ফাইল exists কিনা চেক করুন
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"✅ ক্যাশ লোড হয়েছে: {len(data.get('movies', []))} টি মুভি")
                    return data
            else:
                print("❌ ক্যাশ ফাইল নেই, নতুন তৈরি করছি...")
                # নতুন ফাইল তৈরি করবে
                new_cache = {"movies": [], "last_updated": None}
                self.save_cache()  # ফাইল তৈরি করবে
                return new_cache
        except Exception as e:
            print(f"❌ ক্যাশ লোড এরর: {e}")
            return {"movies": [], "last_updated": None}
    
    def save_cache(self):
        """ক্যাশ ডাটা সেভ করবে"""
        try:
            # ডাটা ফোল্ডার নিশ্চিত করবে
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data, f, ensure_ascii=False, indent=2)
            print(f"✅ ক্যাশ সেভ হয়েছে: {len(self.cache_data['movies'])} টি মুভি")
            print(f"📁 ফাইল লোকেশন: {os.path.abspath(self.cache_file)}")
            return True
        except Exception as e:
            print(f"❌ ক্যাশ সেভ এরর: {e}")
            return False
    
    def update_movies(self, new_movies):
        """নতুন মুভি ডাটা আপডেট করবে - স্মার্ট ডুপ্লিকেট চেক সহ"""
        if not new_movies:
            print("⚠️ আপডেটের জন্য নতুন মুভি নেই")
            return False
        
        existing_movies = self.cache_data["movies"]
        existing_keys = set()
        
        # বর্তমান মুভির keys তৈরি (টাইটেল + ব্লগার সোর্স)
        for movie in existing_movies:
            key = f"{movie['title'].lower()}|{movie.get('blog_source', 'unknown')}"
            existing_keys.add(key)
        
        added_count = 0
        for movie in new_movies:
            # ইউনিক key তৈরি (টাইটেল + ব্লগার সোর্স)
            key = f"{movie['title'].lower()}|{movie.get('blog_source', 'unknown')}"
            
            if key not in existing_keys:
                self.cache_data["movies"].append(movie)
                existing_keys.add(key)
                added_count += 1
        
        self.cache_data["last_updated"] = datetime.now().isoformat()
        self.save_cache()
        print(f"✅ {added_count} টি নতুন মুভি ক্যাশে অ্যাড করা হয়েছে")
        return True
    
    def needs_update(self):
        """ক্যাশ আপডেট প্রয়োজন কিনা চেক করবে (২ ঘন্টা পরপর)"""
        if not self.cache_data.get("last_updated"):
            return True
        
        try:
            last_updated = datetime.fromisoformat(self.cache_data["last_updated"])
            time_diff = datetime.now() - last_updated
            return time_diff > timedelta(hours=2)
        except Exception as e:
            print(f"❌ আপডেট চেক এরর: {e}")
            return True
    
    def get_all_movies(self):
        """সব মুভি রিটার্ন করবে"""
        return self.cache_data.get("movies", [])
    
    def get_movie_count(self):
        """মুভির সংখ্যা রিটার্ন করবে"""
        return len(self.cache_data.get("movies", []))
    
    def search_by_title(self, title):
        """টাইটেল দিয়ে মুভি খুঁজবে"""
        movies = self.cache_data.get("movies", [])
        for movie in movies:
            if movie['title'].lower() == title.lower():
                return movie
        return None
    
    def update_movie_link(self, movie_title, new_detail_link):
        """মুভির লিংক আপডেট করবে"""
        for movie in self.cache_data["movies"]:
            if movie['title'] == movie_title:
                movie['detail_link'] = new_detail_link
                movie['link_updated'] = datetime.now().isoformat()
                self.save_cache()
                print(f"✅ মুভি লিংক আপডেট হয়েছে: {movie_title}")
                return True
        return False

    def get_movie_by_title(self, movie_title):
        """টাইটেল দিয়ে মুভি খুঁজবে"""
        for movie in self.cache_data["movies"]:
            if movie['title'] == movie_title:
                return movie
        return None
    
    def force_refresh_cache(self, blogger_api=None):
        """জোর করে ক্যাশ রিফ্রেশ করবে - ফাইল ডিলিট করে নতুন তৈরি"""
        try:
            print("="*60)
            print("🧹 FORCE ক্যাশ রিফ্রেশ শুরু...")
            
            # ১. ফাইল পাথ
            cache_path = "data/movies_cache.json"
            print(f"📁 ফাইল: {cache_path}")
            
            # ২. ফাইল ডিলিট করব (যদি থাকে)
            if os.path.exists(cache_path):
                os.remove(cache_path)
                print("✅ পুরানো ক্যাশ ফাইল ডিলিট করা হয়েছে")
            else:
                print("ℹ️ ফাইল আগে থেকে নেই")
            
            # ৩. নতুন খালি ক্যাশ ডাটা
            self.cache_data = {
                "movies": [],
                "last_updated": datetime.now().isoformat()
            }
            
            # ৪. যদি blogger_api থাকে, নতুন ডাটা আনব
            new_movies_count = 0
            if blogger_api:
                print("🔄 ব্লগার থেকে নতুন ডাটা আনছি...")
                try:
                    new_movies = blogger_api.get_all_posts_from_all_blogs()
                    if new_movies:
                        self.cache_data["movies"] = new_movies
                        new_movies_count = len(new_movies)
                        print(f"✅ {new_movies_count} টি নতুন মুভি পাওয়া গেছে")
                    else:
                        print("⚠️ ব্লগার থেকে কোনো ডাটা নেই")
                except Exception as e:
                    print(f"⚠️ ব্লগার এরর: {e}")
            
            # ৫. ফাইল সেভ করব
            self.save_cache()
            
            print("🎉 ক্যাশ রিফ্রেশ সম্পূর্ণ!")
            print("="*60)
            
            return True, f"{new_movies_count} টি মুভি"
            
        except Exception as e:
            error_msg = f"রিফ্রেশ ব্যর্থ: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
        
    def fix_all_links_to_desktop(self):
        """ক্যাশের সব লিংককে ডেস্কটপ ভিউতে কনভার্ট করবে"""
        fixed_count = 0
        
        for movie in self.cache_data["movies"]:
            if movie.get('detail_link'):
                old_link = movie['detail_link']
                # ইতিমধ্যে &m=0 থাকলে skip
                if '&m=0' not in old_link and '?m=0' not in old_link:
                    if '?' in old_link:
                        new_link = old_link + '&m=0'
                    else:
                        new_link = old_link + '?m=0'
                    movie['detail_link'] = new_link
                    fixed_count += 1
        
        if fixed_count > 0:
            self.save_cache()
            print(f"✅ {fixed_count} টি মুভির লিংক আপডেট করা হয়েছে")
        
        return fixed_count

# টেস্ট করার জন্য
if __name__ == "__main__":
    cache = CacheManager()
    print(f"মুভি সংখ্যা: {cache.get_movie_count()}")
    print(f"আপডেট প্রয়োজন: {cache.needs_update()}")