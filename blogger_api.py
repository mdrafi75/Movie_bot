# blogger_api.py - ব্লগার API with custom format parsing
import requests
import re
import json
from datetime import datetime

class BloggerAPI:
    def __init__(self, blogs_config):
        self.blogs_config = blogs_config
    
    def get_all_posts_from_all_blogs(self):
        """সব ব্লগার থেকে পোস্ট fetch করবে"""
        all_movies = []
        
        print(f"🔍 ব্লগার থেকে মুভি ডাটা লোড করছি...")
        
        for blog in self.blogs_config:
            try:
                movies = self.get_posts_from_blog(blog)
                all_movies.extend(movies)
                print(f"✅ {blog['name']}: {len(movies)} টি মুভি")
            except Exception as e:
                print(f"❌ {blog['name']} থেকে ডাটা লোড করতে সমস্যা: {e}")
        
        return all_movies
    
    def get_posts_from_blog(self, blog_config):
        """একটি ব্লগার থেকে সব পেজের পোস্ট fetch করবে - পেজিনেশন সহ"""
        all_posts = []
        page_token = None
        page_count = 0
        
        try:
            while True:
                page_count += 1
                # বেস URL
                url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_config['blog_id']}/posts?key={blog_config['api_key']}&maxResults=500"
                
                # পেজ টোকেন যোগ করবে (যদি থাকে)
                if page_token:
                    url += f"&pageToken={page_token}"
                
                print(f"📄 {blog_config['name']} - পেজ {page_count} লোড করছি...")
                
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if 'items' in data:
                    posts_in_page = len(data['items'])
                    all_posts.extend(data['items'])
                    print(f"✅ {blog_config['name']} - পেজ {page_count}: {posts_in_page} টি পোস্ট")
                    
                    # টোটাল পোস্ট সংখ্যা চেক
                    total_items = data.get('totalItems', 'Unknown')
                    print(f"📊 {blog_config['name']} - টোটাল পোস্ট: {total_items}")
                
                # পরবর্তী পেজের টোকেন চেক
                page_token = data.get('nextPageToken')
                
                # যদি আর টোকেন না থাকে, লুপ ব্রেক করবে
                if not page_token:
                    print(f"🏁 {blog_config['name']} - সব পেজ লোড সম্পূর্ণ: {len(all_posts)} টি পোস্ট")
                    break
                    
                # সেফটি ব্রেক - সর্বোচ্চ ১০ পেজ
                if page_count >= 10:
                    print(f"⚠️ {blog_config['name']} - সর্বোচ্চ ১০ পেজ লোড করা হয়েছে")
                    break
                    
            # পোস্টগুলো প্রসেস করে মুভি ডাটা বের করবে
            movies = []
            for post in all_posts:
                movie_data = self.extract_movie_from_custom_format(post, blog_config['name'])
                if movie_data:
                    movies.append(movie_data)

            print(f"🎬 {blog_config['name']}: {len(movies)} টি ভ্যালিড মুভি")
            return movies
                    
        except Exception as e:
            print(f"❌ {blog_config['name']} API এরর: {e}")
            return []  # এরর হলে খালি লিস্ট রিটার্ন করবে
    
    def extract_movie_from_custom_format(self, post, blog_name):
        """মুভি ডাটার সাথে ইমেজ URL ও এক্সট্রাক্ট করবে"""
        try:
            content = post['content']
            
            # MOVIE_DATA_START এবং MOVIE_DATA_END এর মধ্যে ডাটা extract করবে
            movie_block = self.extract_between(content, "MOVIE_DATA_START", "MOVIE_DATA_END")
            
            if not movie_block:
                print(f"⚠️ MOVIE_DATA_BLOCK নেই: {post['title'][:50]}...")
                return None
            
            # শুধু প্রয়োজনীয় ৫টি metadata extract করবে (বছর যোগ হয়েছে)
            title = self.extract_value(movie_block, "MOVIE_TITLE:")
            
            # রেটিং extract - মাল্টি ফরম্যাট
            rating = self.extract_value(movie_block, "MOVIE_RATING:")
            if not rating:
                rating = self.extract_value(movie_block, "RATING:")
            
            # কোয়ালিটি extract - মাল্টি ফরম্যাট  
            quality = self.extract_value(movie_block, "MOVIE_QUALITY:")
            if not quality:
                quality = self.extract_value(movie_block, "QUALITY:")
            
            # ✅ বছর extract - মাল্টি ফরম্যাট
            year = self.extract_value(movie_block, "MOVIE_YEAR:")
            if not year:
                year = self.extract_value(movie_block, "YEAR:")
            if not year:
                year = self.extract_value(movie_block, "RELEASE_YEAR:")
            if not year:
                year = self.extract_value(movie_block, "RELEASE_DATE:")
            
            # ✅ যদি মেটাডাটায় বছর না থাকে, টাইটেল থেকে extract করবে
            if not year:
                year = self.extract_year_from_title(post['title'])
            
            detail_link = self.extract_detail_link(movie_block)
            
            if not title:
                print(f"⚠️ MOVIE_TITLE নেই: {post['title'][:50]}...")
                return None
            
            # ✅ নতুন: ইমেজ URL extract করবে
            image_url = self.extract_image_url(content)
            
            movie_data = {
                'title': title.strip(),
                'rating': rating.strip() if rating else "",
                'quality': quality.strip() if quality else "HD",
                'year': year.strip() if year else "",  # ✅ বছর যোগ হয়েছে
                'detail_link': detail_link,
                'blog_source': blog_name,
                'blogger_url': post['url'],
                'published_date': post['published'],
                'image_url': image_url
            }
            
            print(f"✅ মুভি ডাটা: {title[:30]}... | রেটিং: {movie_data['rating']} | বছর: {movie_data['year']} | ইমেজ: {'✅' if image_url else '❌'}")
            return movie_data
            
        except Exception as e:
            print(f"⚠️ পোস্ট প্রসেস করতে সমস্যা: {e}")
            return None

    def extract_year_from_title(self, title):
        """টাইটেল থেকে বছর extract করবে"""
        try:
            import re
            # প্যাটার্ন: (2019), [2020], 2021, 2023, ইত্যাদি
            patterns = [
                r'\((\d{4})\)',      # (2019)
                r'\[(\d{4})\]',      # [2020]  
                r'\b(19\d{2})\b',    # 1999
                r'\b(20\d{2})\b',    # 2023
            ]
            
            for pattern in patterns:
                match = re.search(pattern, title)
                if match:
                    year = match.group(1) if '(' in pattern or '[' in pattern else match.group()
                    print(f"    📅 টাইটেল থেকে বছর পাওয়া গেছে: {year}")
                    return year
            
            return ""
        except Exception as e:
            print(f"    ❌ বছর extract এরর: {e}")
            return ""

    def extract_image_url(self, content):
        """HTML content থেকে প্রথম ইমেজ (পোস্টার) extract করবে"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # প্রথম separator div খুঁজবে (যেখানে পোস্টার থাকে)
            first_separator = soup.find('div', class_='separator')
            
            if first_separator:
                # প্রথম img tag খুঁজবে
                img_tag = first_separator.find('img')
                if img_tag and img_tag.get('src'):
                    image_url = img_tag['src']
                    print(f"    🖼️ পোস্টার ইমেজ পাওয়া গেছে: {image_url[:80]}...")
                    return image_url
            
            print("    ⚠️ কোনো পোস্টার ইমেজ পাওয়া যায়নি")
            return None
            
        except Exception as e:
            print(f"    ❌ ইমেজ extract এরর: {e}")
            return None
    
    def extract_between(self, text, start_marker, end_marker):
        """দুটি marker-এর মধ্যে text extract করবে"""
        try:
            start_index = text.find(start_marker)
            if start_index == -1:
                return None
            
            start_index += len(start_marker)
            end_index = text.find(end_marker, start_index)
            
            if end_index == -1:
                return None
            
            return text[start_index:end_index].strip()
        except:
            return None
    
    def extract_value(self, text, key):
        """Key থেকে value extract করবে"""
        try:
            pattern = key + r'\s*(.*?)(?=\n|$)'
            match = re.search(pattern, text)
            return match.group(1).strip() if match else None
        except:
            return None
    
    
    def extract_detail_link(self, movie_block):
        """DETAIL_LINK extract করবে এবং ডেস্কটপ ভিউ প্যারামিটার যোগ করবে"""
        try:
            if 'DETAIL_LINK:' in movie_block:
                start_idx = movie_block.find('DETAIL_LINK:') + len('DETAIL_LINK:')
                remaining = movie_block[start_idx:].strip()
                lines = remaining.split('\n')
                if lines:
                    link = lines[0].strip()
                    if link and link.startswith('http'):
                        # ✅ নতুন: ডেস্কটপ ভিউ প্যারামিটার যোগ
                        link = self.add_desktop_param(link)
                        print(f"    ✅ DETAIL_LINK (ডেস্কটপ): {link[:80]}...")
                        return link
            return None
        except Exception as e:
            print(f"    ❌ Link extract error: {e}")
            return None
        
    def add_desktop_param(self, link):
        """ডিটেইল লিংকে &m=0 প্যারামিটার যোগ করবে"""
        if not link:
            return link
        
        # ইতিমধ্যে &m=0 বা ?m=0 থাকলে কিছু করব না
        if '&m=0' in link or '?m=0' in link:
            return link
        
        # যদি লিংকে ? থাকে (অর্থাৎ প্যারামিটার আছে)
        if '?' in link:
            # ?m=1 থাকলে সরিয়ে &m=0 যোগ করব
            if '?m=1' in link:
                link = link.replace('?m=1', '')
            # অন্যান্য প্যারামিটারের সাথে &m=0 যোগ
            if '?' in link and not link.endswith('&'):
                link = link + '&m=0'
            else:
                link = link + 'm=0'
        else:
            # কোনো প্যারামিটার না থাকলে ?m=0 যোগ
            link = link + '?m=0'
        
        print(f"   🔄 ডেস্কটপ লিংক তৈরি: {link[:80]}...")
        return link
        

