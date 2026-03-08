# request_manager.py - মুভি রিকোয়েস্ট ম্যানেজমেন্ট সিস্টেট
import json
import os
from datetime import datetime, timedelta
import re

class RequestManager:
    def __init__(self, request_file="data/movie_requests.json"):
        self.request_file = request_file
        self.requests_data = self.load_requests()
    
    def load_requests(self):
        """রিকোয়েস্ট ডাটা লোড করবে"""
        try:
            os.makedirs(os.path.dirname(self.request_file), exist_ok=True)
            
            if os.path.exists(self.request_file):
                with open(self.request_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"✅ রিকোয়েস্ট ডাটা লোড হয়েছে: {len(data.get('requests', []))} টি")
                    return data
            else:
                print("❌ রিকোয়েস্ট ফাইল নেই, নতুন তৈরি করছি...")
                new_data = {
                    "requests": [],
                    "last_request_id": 0,
                    "stats": {
                        "total_requests": 0,
                        "fulfilled": 0,
                        "pending": 0
                    }
                }
                self.save_requests(new_data)
                return new_data
        except Exception as e:
            print(f"❌ রিকোয়েস্ট লোড এরর: {e}")
            return {"requests": [], "last_request_id": 0, "stats": {"total_requests": 0, "fulfilled": 0, "pending": 0}}
    
    def save_requests(self, data=None):
        """রিকোয়েস্ট ডাটা সেভ করবে"""
        try:
            data_to_save = data or self.requests_data
            os.makedirs(os.path.dirname(self.request_file), exist_ok=True)
            
            with open(self.request_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
            print(f"✅ রিকোয়েস্ট সেভ হয়েছে: {len(data_to_save['requests'])} টি")
            return True
        except Exception as e:
            print(f"❌ রিকোয়েস্ট সেভ এরর: {e}")
            return False
    
    def extract_movie_info(self, text):
        """রিকোয়েস্ট টেক্সট থেকে মুভি নাম ও সাল extract করবে"""
        try:
            # কমান্ড অংশ রিমুভ
            text = re.sub(r'^(/request|/req|request|req)\s+', '', text, flags=re.IGNORECASE)
            text = text.strip()
            
            # সাল extract (শেষে থাকলে)
            year_match = re.search(r'\b(19|20)\d{2}\b', text)
            year = year_match.group() if year_match else ""
            
            # সাল রিমুভ করে মুভি নাম নিবে
            movie_name = re.sub(r'\b(19|20)\d{2}\b', '', text).strip()
            
            return {
                'movie_name': movie_name,
                'year': year,
                'full_query': f"{movie_name} {year}".strip()
            }
        except Exception as e:
            print(f"❌ মুভি info extract এরর: {e}")
            return {'movie_name': text, 'year': '', 'full_query': text}
    
    def add_request(self, user_id, username, full_name, movie_query):
        """নতুন রিকোয়েস্ট যোগ করবে"""
        try:
            movie_info = self.extract_movie_info(movie_query)
            
            request_id = self.requests_data['last_request_id'] + 1
            request_data = {
                'request_id': request_id,
                'movie_name': movie_info['movie_name'],
                'movie_year': movie_info['year'],
                'full_query': movie_info['full_query'],
                'user_id': user_id,
                'username': username or f"user_{user_id}",
                'full_name': full_name,
                'status': 'pending',  # pending, fulfilled, rejected
                'request_time': datetime.now().isoformat(),
                'fulfilled_time': None,
                'notification_sent': False
            }
            
            self.requests_data['requests'].append(request_data)
            self.requests_data['last_request_id'] = request_id
            self.requests_data['stats']['total_requests'] += 1
            self.requests_data['stats']['pending'] += 1
            
            self.save_requests()
            
            print(f"✅ নতুন রিকোয়েস্ট যোগ করা হয়েছে: #{request_id} - {movie_info['full_query']}")
            return request_data
            
        except Exception as e:
            print(f"❌ রিকোয়েস্ট যোগ করতে সমস্যা: {e}")
            return None
    
    def mark_fulfilled(self, request_id):
        """রিকোয়েস্ট fulfilled মার্ক করবে"""
        try:
            for request in self.requests_data['requests']:
                if request['request_id'] == request_id:
                    request['status'] = 'fulfilled'
                    request['fulfilled_time'] = datetime.now().isoformat()
                    request['notification_sent'] = True
                    
                    self.requests_data['stats']['fulfilled'] += 1
                    self.requests_data['stats']['pending'] -= 1
                    
                    self.save_requests()
                    print(f"✅ রিকোয়েস্ট fulfilled: #{request_id}")
                    return True
            
            print(f"❌ রিকোয়েস্ট পাওয়া যায়নি: #{request_id}")
            return False
        except Exception as e:
            print(f"❌ fulfilled মার্ক করতে সমস্যা: {e}")
            return False
    
    def get_user_requests(self, user_id):
        """ইউজারের সব রিকোয়েস্ট দেখাবে"""
        user_requests = []
        for request in self.requests_data['requests']:
            if str(request['user_id']) == str(user_id):
                user_requests.append(request)
        
        return sorted(user_requests, key=lambda x: x['request_id'], reverse=True)
    
    def get_pending_requests(self):
        """সব পেন্ডিং রিকোয়েস্ট দেখাবে"""
        return [r for r in self.requests_data['requests'] if r['status'] == 'pending']
    
    def check_user_limit(self, user_id, max_per_day=5):
        """ইউজারের দৈনিক লিমিট চেক করবে"""
        try:
            today = datetime.now().date()
            user_requests_today = 0
            
            for request in self.requests_data['requests']:
                if str(request['user_id']) == str(user_id):
                    request_date = datetime.fromisoformat(request['request_time']).date()
                    if request_date == today:
                        user_requests_today += 1
            
            return user_requests_today < max_per_day, max_per_day - user_requests_today
        except:
            return True, max_per_day
    
    def check_duplicate_request(self, user_id, movie_query):
        """ডুপ্লিকেট রিকোয়েস্ট চেক করবে"""
        try:
            movie_info = self.extract_movie_info(movie_query)
            
            for request in self.requests_data['requests']:
                if (str(request['user_id']) == str(user_id) and 
                    request['full_query'].lower() == movie_info['full_query'].lower() and
                    request['status'] == 'pending'):
                    return True, request
            
            return False, None
        except:
            return False, None
        
    def cleanup_successful_requests(self, days_old=15):
        """সফল রিকোয়েস্ট ১৫ দিন পর ডিলেট করবে"""
        try:
            from datetime import datetime, timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            initial_count = len(self.requests_data['requests'])
            
            # শুধু পেন্ডিং রিকোয়েস্ট এবং ১৫ দিনের মধ্যে সফল রিকোয়েস্ট রাখবে
            filtered_requests = []
            deleted_count = 0
            
            for req in self.requests_data['requests']:
                req_time = datetime.fromisoformat(req['request_time'])
                
                # ❌ ১৫ দিনের পুরানো সফল রিকোয়েস্ট ডিলেট করবে
                if req['status'] == 'fulfilled' and req_time < cutoff_date:
                    deleted_count += 1
                    continue
                
                # ✅ পেন্ডিং সবসময় রাখবে
                # ✅ ১৫ দিনের মধ্যে সফল রিকোয়েস্ট রাখবে
                filtered_requests.append(req)
            
            # আপডেট করব
            self.requests_data['requests'] = filtered_requests
            
            # স্ট্যাটস আপডেট
            if deleted_count > 0:
                self.requests_data['stats']['total_requests'] = len(filtered_requests)
                self.requests_data['stats']['fulfilled'] = sum(
                    1 for r in filtered_requests if r['status'] == 'fulfilled'
                )
                self.requests_data['stats']['pending'] = sum(
                    1 for r in filtered_requests if r['status'] == 'pending'
                )
                
                self.save_requests()
                print(f"🧹 {deleted_count} টি পুরানো সফল রিকোয়েস্ট ডিলেট করা হয়েছে (১৫+ দিন)")
            
            return deleted_count
            
        except Exception as e:
            print(f"❌ রিকোয়েস্ট ক্লিনআপ এরর: {e}")
            return 0
        
    def mark_rejected(self, request_id):
        """রিকোয়েস্ট rejected মার্ক করবে"""
        try:
            for request in self.requests_data['requests']:
                if request['request_id'] == request_id:
                    request['status'] = 'rejected'
                    request['rejected_time'] = datetime.now().isoformat()
                    
                    self.requests_data['stats']['pending'] -= 1
                    # rejected স্ট্যাটস যোগ করতে চাইলে আলাদা কাউন্টার রাখতে হবে
                    
                    self.save_requests()
                    print(f"❌ রিকোয়েস্ট rejected: #{request_id}")
                    return True
            
            print(f"❌ রিকোয়েস্ট পাওয়া যায়নি: #{request_id}")
            return False
        except Exception as e:
            print(f"❌ rejected মার্ক করতে সমস্যা: {e}")
            return False

# টেস্ট করার জন্য
if __name__ == "__main__":
    rm = RequestManager()
    print(f"টোটাল রিকোয়েস্ট: {rm.requests_data['stats']['total_requests']}")