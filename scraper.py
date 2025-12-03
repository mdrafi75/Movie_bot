# scraper.py - ফিক্সড ওয়েব স্ক্রেপিং সিস্টেম
import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime

class MovieScraper:
    def __init__(self, website_url):
        self.website_url = website_url
        self.movies_data = []
    
    def scrape_movies(self):
        """ওয়েবসাইট থেকে আসল মুভি ডাটা স্ক্রেপ করবে"""
        try:
            print(f"🔍 স্ক্রেপিং শুরু: {self.website_url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(self.website_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            print("✅ ওয়েবসাইট লোড হয়েছে")
            
            # আপনার সাইটের জন্য সঠিক elements খুঁজবে
            # Test থেকে দেখলাম: 96 div, 103 links
            all_links = soup.find_all('a')
            print(f"🔗 মোট লিংক: {len(all_links)} টি")
            
            movie_count = 0
            
            # শুধু relevant links filter করবে
            for link in all_links:
                try:
                    href = link.get('href', '')
                    link_text = link.text.strip()
                    
                    # শুধু valid movie links নেবে
                    if self.is_movie_link(link_text, href):
                        movie_data = {
                            'title': self.clean_title(link_text),
                            'year': self.extract_year_from_text(link_text),
                            'quality': self.extract_quality_from_text(link_text),
                            'link': self.make_absolute_url(href)
                        }
                        
                        if movie_data['title'] and len(movie_data['title']) > 3:
                            self.movies_data.append(movie_data)
                            movie_count += 1
                            print(f"✅ মুভি {movie_count}: {movie_data['title']}")
                            
                except Exception as e:
                    continue
            
            # যদি movie না পায়, তাহলে headings থেকে খুঁজবে
            if movie_count == 0:
                print("🔍 লিংক থেকে মুভি না পেয়ে headings check করছি...")
                headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                for heading in headings:
                    try:
                        title = heading.text.strip()
                        if self.is_movie_title(title):
                            movie_data = {
                                'title': self.clean_title(title),
                                'year': self.extract_year_from_text(title),
                                'quality': self.extract_quality_from_text(title),
                                'link': self.website_url
                            }
                            
                            if movie_data['title'] and len(movie_data['title']) > 3:
                                self.movies_data.append(movie_data)
                                movie_count += 1
                                print(f"✅ মুভি {movie_count}: {movie_data['title']}")
                                
                    except Exception as e:
                        continue
            
            print(f"✅ স্ক্রেপিং সম্পূর্ণ: {movie_count} টি মুভি পাওয়া গেছে")
            return self.movies_data
            
        except Exception as e:
            print(f"❌ স্ক্রেপিং এরর: {e}")
            return []

    def is_movie_link(self, link_text, href):
        """লিংকটি মুভি লিংক কিনা চেক করবে"""
        if not link_text or len(link_text) < 5:
            return False
        
        # Common non-movie texts exclude করবে
        exclude_texts = ['home', 'login', 'facebook', 'telegram', 'twitter', 'instagram', 
                        'contact', 'about', 'privacy', 'terms', 'movie bazar', 'mbbd']
        
        if any(exclude in link_text.lower() for exclude in exclude_texts):
            return False
        
        # শুধু valid-looking titles নেবে
        if len(link_text) > 20 and any(char.isdigit() for char in link_text):
            return True
            
        return len(link_text) > 10

    def is_movie_title(self, text):
        """টেক্সটটি মুভি টাইটেল কিনা চেক করবে"""
        if not text or len(text) < 10:
            return False
        
        # Common non-movie texts exclude করবে
        exclude_texts = ['movie bazar', 'mbbd', 'home', 'login', 'welcome']
        
        if any(exclude in text.lower() for exclude in exclude_texts):
            return False
        
        return True

    def clean_title(self, title):
        """টাইটেল ক্লিন করবে"""
        if not title:
            return ""
        
        # Extra spaces এবং newlines remove করবে
        title = ' '.join(title.split())
        
        # Very long titles trim করবে
        if len(title) > 100:
            title = title[:100] + "..."
            
        return title

    def extract_year_from_text(self, text):
        """টেক্সট থেকে সাল extract করবে"""
        try:
            year_match = re.search(r'\b(20[0-2][0-9]|19[0-9]{2})\b', text)
            return year_match.group() if year_match else "2024"
        except:
            return "2024"

    def extract_quality_from_text(self, text):
        """টেক্সট থেকে quality extract করবে"""
        try:
            text_upper = text.upper()
            if any(q in text_upper for q in ['4K', 'UHD', '2160P']):
                return '4K'
            elif any(q in text_upper for q in ['1080P', 'FHD']):
                return '1080p'
            elif any(q in text_upper for q in ['720P', 'HD']):
                return '720p'
            else:
                return 'HD'
        except:
            return 'HD'

    def make_absolute_url(self, href):
        """Relative URL কে absolute URL-এ convert করবে"""
        if not href or href == '#':
            return self.website_url
            
        if href.startswith('http'):
            return href
        elif href.startswith('/'):
            return f"https://mbbd2.blogspot.com{href}"
        else:
            return f"https://mbbd2.blogspot.com/{href}"

# টেস্ট করার জন্য
if __name__ == "__main__":
    scraper = MovieScraper("https://mbbd2.blogspot.com/?m=0")
    movies = scraper.scrape_movies()
    
    if movies:
        print(f"\n🎬 স্ক্রেপ করা মুভি লিস্ট:")
        for i, movie in enumerate(movies[:10], 1):  # শুধু প্রথম ১০টি দেখাবে
            print(f"{i}. {movie['title']} ({movie['year']}) - {movie['quality']}")
        if len(movies) > 10:
            print(f"... এবং আরও {len(movies) - 10} টি মুভি")
    else:
        print("❌ কোনো মুভি স্ক্রেপ করা যায়নি")