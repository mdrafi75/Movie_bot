# search_engine.py - এডভান্সড সার্চ সিস্টেম (ফিক্সড ভার্সন)
import re
import difflib

# Try to import fuzzywuzzy, but provide fallback
try:
    from fuzzywuzzy import fuzz, process
    FUZZY_AVAILABLE = True
    print("✅ fuzzywuzzy লোড হয়েছে")
except ImportError:
    print("⚠️ fuzzywuzzy না থাকলে alternative ব্যবহার করবে")
    FUZZY_AVAILABLE = False

class SearchEngine:
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
    
    def search_movies(self, query):
        """মুভি সার্চ করবে - বাংলা এবং ইংলিশ উভয় ভাষায়"""
        if not query or not query.strip():
            return []
            
        query = query.strip().lower()
        movies = self.cache_manager.get_all_movies()
        
        if not movies:
            print("⚠️ ক্যাশে কোনো মুভি নেই")
            return []
        
        results = []
        
        for movie in movies:
            score = self.calculate_match_score(movie, query)

            if movie.get('year') and movie['year'] in query:
                score += 30  # বছর ম্যাচ বোনাস

            if score >= 50:  # 50% এর বেশি ম্যাচ হলে
                results.append({
                    'movie': movie,
                    'score': score
                })
        
        # স্কোর অনুযায়ী সাজাবে (উচ্চ স্কোর প্রথমে)
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # শুধু মুভি objects রিটার্ন করবে
        search_results = [result['movie'] for result in results]
        
        print(f"🔍 সার্চ: '{query}' → {len(search_results)} টি রেজাল্ট")
        return search_results
    
    def calculate_match_score(self, movie, query):
        """ম্যাচ স্কোর ক্যালকুলেট করবে - বাংলা এবং ইংলিশ উভয় ভাষায়"""
        
        # ✅ NEW: আগে এক্সাক্ট ম্যাচ চেক করব
        query_lower = query.lower().strip()
        title_lower = movie.get('title', '').lower().strip()
        
        # 1. EXACT MATCH (মূল সমস্যা এখানে)
        if query_lower == title_lower:
            return 100  # ✅ সরাসরি 100%
        
        # 2. QUERY টাইটেলে আছে (বা উল্টো)
        if query_lower in title_lower or title_lower in query_lower:
            return 95  # ✅ 95%
        
        # 3. Word-by-word এক্সাক্ট ম্যাচ
        query_words = set(query_lower.split())
        title_words = set(title_lower.split())
        
        if query_words == title_words:
            return 90  # ✅ 90%
        
        # 4. তারপর আগের লজিক
        scores = []
        
        # ইংলিশ টাইটেলে সার্চ
        if movie.get('title'):
            title_score = self.fuzzy_ratio(query, movie['title'].lower())
            scores.append(title_score)
        
        # বাংলা টাইটেলে সার্চ
        if movie.get('bangla_title'):
            bangla_score = self.fuzzy_ratio(query, movie['bangla_title'].lower())
            scores.append(bangla_score)
        
        # সিরিজ ম্যাচিং (Dhoom, Dhoom 2, Dhoom 3)
        series_score = self.check_series_match(movie, query)
        if series_score > 0:
            scores.append(series_score)
        
        # ✅ নতুন: শব্দ ভিত্তিতে ম্যাচ স্কোর (অটো সার্চের জন্য)
        word_based_score = self.calculate_word_based_score(movie, query)
        scores.append(word_based_score)
        
        return max(scores) if scores else 0
    
    def fuzzy_ratio(self, str1, str2):
        """Fuzzy ratio calculator - fuzzywuzzy না থাকলে alternative ব্যবহার করবে"""
        if FUZZY_AVAILABLE:
            return fuzz.partial_ratio(str1, str2)
        else:
            # Alternative fuzzy matching
            return self.simple_ratio(str1, str2)
    
    # এই ফাংশনটি REPLACE করবেন:
    def simple_ratio(self, str1, str2):
        """সিম্পল রেশিও ক্যালকুলেটর - FIXED"""
        if not str1 or not str2:
            return 0  # ✅ 0 দিচ্ছে, 0.0 নয়
        
        str1 = str1.lower()
        str2 = str2.lower()
        
        # Exact match
        if str1 == str2:
            return 100  # ✅ 100%
        
        # Basic partial matching
        if str1 in str2 or str2 in str1:
            return 90  # ✅ 90% (VS Code-এ 95 ছিল)
        
        # Word-based matching
        str1_words = set(str1.split())
        str2_words = set(str2.split())
        common_words = str1_words.intersection(str2_words)
        
        if common_words:
            match_percentage = (len(common_words) / max(len(str1_words), len(str2_words))) * 100
            return int(min(85, match_percentage))  # ✅ Max 85%
        
        # Character-based similarity using difflib
        try:
            similarity = difflib.SequenceMatcher(None, str1, str2).ratio()
            return int(similarity * 100)  # ✅ 100% পর্যন্ত স্কেল করছি
        except:
            # Fallback: common characters
            common_chars = set(str1) & set(str2)
            if not common_chars:
                return 0
            similarity = len(common_chars) / max(len(str1), len(str2))
        return int(similarity * 80)  # ✅ 80% পর্যন্ত
    
    def check_series_match(self, movie, query):
        """সিরিজ ম্যাচিং চেক করবে (Dhoom, Dhoom 2, ইত্যাদি)"""
        # মুভি টাইটেল থেকে বেস নাম বের করবে
        base_title = self.extract_base_title(movie['title'])
        query_base = self.extract_base_title(query)
        
        if base_title and query_base:
            return self.fuzzy_ratio(query_base.lower(), base_title.lower())
        return 0
    
    def extract_base_title(self, title):
        """টাইটেল থেকে বেস নাম বের করবে (স্মার্ট ভার্সন)"""
        if not title:
            return ""
        
        # Original title সংরক্ষণ
        original_title = title.strip()
        
        # ১. প্রথমে মুভির সাল (year) রিমুভ করবে
        # প্যাটার্ন: (2019), 2023, 1999, 2020, etc.
        title_no_year = re.sub(r'\s*[\(\[]?\b(19|20)\d{2}\b[\)\]]?', '', original_title)
        
        # ২. কোয়ালিটি ট্যাগ রিমুভ (HD, 1080p, 4K, etc.)
        quality_tags = ['HD', '720p', '1080p', '4K', 'FHD', 'UHD', 'BluRay', 'DVD', 'WEB-DL', 'WEBRip', 'HDRip']
        for tag in quality_tags:
            title_no_year = re.sub(fr'\s*{tag}\s*', ' ', title_no_year, flags=re.IGNORECASE)
        
        # ৩. কমন মুভি ফরম্যাট রিমুভ
        patterns_to_remove = [
            r'\s*\(.*\)',  # বন্ধনীর ভিতরের কিছু
            r'\s*\[.*\]',  # ব্র্যাকেটের ভিতরের কিছু
            r'\s*-\s*.*$',  # ড্যাশের পরের অংশ
            r'\s*–\s*.*$',  # এন ড্যাশের পরের অংশ
        ]
        
        for pattern in patterns_to_remove:
            title_no_year = re.sub(pattern, '', title_no_year)
        
        title_clean = title_no_year.strip()
        
        # ৪. সিরিজ/পার্ট ডিটেকশন - মাল্টিপল প্যাটার্ন
        series_patterns = [
            # প্যাটার্ন ১: "Dhoom 2" → "Dhoom"
            (r'^(.+?)\s+(?:part|pt|chapter|ch|episode|ep)\s*[0-9IVX]+$', 1, re.IGNORECASE),
            
            # প্যাটার্ন ২: "Dhoom 2" → "Dhoom" (শুধু সংখ্যা)
            (r'^(.+?)\s+[0-9]+$', 1),
            
            # প্যাটার্ন ৩: "Dhoom II" → "Dhoom" (রোমান সংখ্যা)
            (r'^(.+?)\s+[IVX]+$', 1),
            
            # প্যাটার্ন ৪: "Dhoom: Part 2" → "Dhoom"
            (r'^(.+?)\s*[:·]\s*(?:part|pt)\s*[0-9]+$', 1, re.IGNORECASE),
            
            # প্যাটার্ন ৫: "The Avengers 2012" → "The Avengers" (বছর আলাদা)
            (r'^(.+?)\s+(?:19|20)\d{2}$', 1),
        ]
        
        for pattern, group_idx, *flags in series_patterns:
            regex_flags = re.IGNORECASE if flags and 're.IGNORECASE' in str(flags) else 0
            match = re.match(pattern, title_clean, regex_flags)
            if match:
                base_title = match.group(group_idx).strip()
                
                # বেস টাইটেল যাচাই করবে (খালি বা খুব ছোট না হলে)
                if base_title and len(base_title) >= 2:
                    # শেষের দিকের সংখ্যা/রোমান সংখ্যা চেক
                    if re.search(r'\s+[0-9IVX]+$', base_title):
                        base_title = re.sub(r'\s+[0-9IVX]+$', '', base_title).strip()
                    
                    return base_title
        
        # ৫. শেষ চেষ্টা: শুধু শব্দগুলো নেবে (বছর, সংখ্যা, কোয়ালিটি বাদ)
        words = title_clean.split()
        filtered_words = []
        
        for word in words:
            # সংখ্যা/বছর চেক
            if re.match(r'^\d+$', word) or re.match(r'^(19|20)\d{2}$', word):
                continue
            # রোমান সংখ্যা চেক
            if re.match(r'^[IVX]+$', word, re.IGNORECASE):
                continue
            # কোয়ালিটি শব্দ চেক
            if word.upper() in [q.upper() for q in quality_tags]:
                continue
            
            filtered_words.append(word)
        
        if filtered_words:
            return ' '.join(filtered_words)
        
        # সব ব্যর্থ হলে original টাইটেল রিটার্ন
        return original_title
    
    def calculate_word_based_score(self, movie, query):
        """শব্দ ভিত্তিতে ম্যাচ স্কোর ক্যালকুলেট করবে"""
        try:
            query_words = set(query.lower().split())
            title_words = set(movie['title'].lower().split())
            
            # কমন শব্দ খুঁজবে
            common_words = query_words.intersection(title_words)
            
            if not common_words:
                return 0
                
            # স্কোর ক্যালকুলেট
            match_ratio = len(common_words) / max(len(query_words), len(title_words))
            return int(match_ratio * 100)
            
        except:
            return 0
    
    def find_similar_movies(self, query):
        """স্পেলিং করেকশনের জন্য সিমিলার মুভি খুঁজবে"""
        movies = self.cache_manager.get_all_movies()
        similar_movies = []
        
        for movie in movies:
            # ইংলিশ টাইটেলে ম্যাচ
            title_score = self.fuzzy_ratio(query.lower(), movie['title'].lower())
            
            # বাংলা টাইটেলে ম্যাচ
            bangla_score = 0
            if movie.get('bangla_title'):
                bangla_score = self.fuzzy_ratio(query.lower(), movie['bangla_title'].lower())
            
            best_score = max(title_score, bangla_score)
            
            # 60-95% ম্যাচ (সম্পূর্ণ ম্যাচ না)
            if 60 <= best_score < 95:
                similar_movies.append(movie)
        
        # সর্বোচ্চ ৩টি সিমিলার মুভি রিটার্ন করবে
        return similar_movies[:3]
    
    def get_movie_series(self, movie_title):
        """একই সিরিজের সব মুভি খুঁজবে - ইমপ্রুভড ভার্সন"""
        # প্রথমে বেস টাইটেল বের করবে
        base_title = self.extract_base_title(movie_title)
        
        if not base_title:
            return []
        
        movies = self.cache_manager.get_all_movies()
        series_movies = []
        
        print(f"🔍 সিরিজ সার্চ: '{movie_title}' → বেস: '{base_title}'")
        
        for movie in movies:
            current_title = movie['title']
            current_base = self.extract_base_title(current_title)
            
            # বেস টাইটেল ম্যাচ করলে
            if current_base and current_base.lower() == base_title.lower():
                # পার্ট নম্বর এক্সট্রাক্ট করবে
                part_number = self.extract_part_number(current_title)
                movie_with_part = movie.copy()
                movie_with_part['part_number'] = part_number
                movie_with_part['base_title'] = base_title
                
                series_movies.append(movie_with_part)
                print(f"   ✅ সিরিজে যোগ: {current_title} (পার্ট: {part_number})")
        
        # পার্ট নম্বর অনুযায়ী সাজাবে
        if series_movies:
            series_movies.sort(key=lambda x: (
                x['part_number'] is None,  # None গুলো শেষে
                x['part_number'] if x['part_number'] is not None else float('inf')
            ))
            print(f"🎬 '{base_title}' সিরিজে {len(series_movies)} টি মুভি পাওয়া গেছে")
        
        return series_movies
    
    def extract_part_number(self, title):
        """মুভি টাইটেল থেকে পার্ট নম্বর বের করবে"""
        if not title:
            return None
        
        # বিভিন্ন প্যাটার্ন চেক করবে
        patterns = [
            (r'.*\b(?:part|pt|chapter|ch|episode|ep)\s*(\d+)\b', 1),  # Part 2, Episode 3
            (r'.*\s+(\d+)\b', 1),  # শুধু সংখ্যা (Dhoom 2)
            (r'.*\b([IVX]+)\b', 1),  # রোমান সংখ্যা (II, III)
        ]
        
        for pattern, group_idx in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                part_str = match.group(group_idx)
                
                # রোমান সংখ্যাকে ডেসিমালে কনভার্ট
                if re.match(r'^[IVX]+$', part_str, re.IGNORECASE):
                    return self.roman_to_decimal(part_str.upper())
                
                # সংখ্যা হলে ইন্টিজারে কনভার্ট
                try:
                    return int(part_str)
                except:
                    continue
        
        return None
    
    def roman_to_decimal(self, roman):
        """রোমান সংখ্যাকে ডেসিমালে কনভার্ট করবে"""
        roman_numerals = {
            'I': 1, 'V': 5, 'X': 10, 'L': 50,
            'C': 100, 'D': 500, 'M': 1000
        }
        
        total = 0
        prev_value = 0
        
        for char in reversed(roman):
            value = roman_numerals.get(char, 0)
            if value < prev_value:
                total -= value
            else:
                total += value
            prev_value = value
        
        return total
    
    def find_all_series_movies(self):
        """সব সিরিজ মুভি খুঁজে রিটার্ন করবে - ডিবাগিং এর জন্য"""
        movies = self.cache_manager.get_all_movies()
        series_dict = {}
        
        for movie in movies:
            base_title = self.extract_base_title(movie['title'])
            if base_title:
                if base_title not in series_dict:
                    series_dict[base_title] = []
                series_dict[base_title].append(movie)
        
        # শুধু সেই সিরিজগুলো রিটার্ন করবে যেগুলোর ১টির বেশি মুভি আছে
        multi_part_series = {k: v for k, v in series_dict.items() if len(v) > 1}
        
        print(f"\n📊 সিরিজ রিপোর্ট:")
        print(f"   মোট মুভি: {len(movies)} টি")
        print(f"   ইউনিক বেস টাইটেল: {len(series_dict)} টি")
        print(f"   মাল্টি-পার্ট সিরিজ: {len(multi_part_series)} টি")
        
        # শীর্ষ ৫টি সিরিজ প্রিন্ট করবে
        for i, (base_title, series_movies) in enumerate(list(multi_part_series.items())[:5]):
            print(f"   {i+1}. '{base_title}': {len(series_movies)} টি পার্ট")
            for movie in series_movies[:3]:
                print(f"      - {movie['title']}")
            if len(series_movies) > 3:
                print(f"      ... এবং আরও {len(series_movies)-3} টি")
        
        return multi_part_series

# টেস্ট করার জন্য
if __name__ == "__main__":
    from cache_manager import CacheManager
    
    # ক্যাশ ম্যানেজার তৈরি
    cache = CacheManager()
    
    # সার্চ ইঞ্জিন তৈরি
    search_engine = SearchEngine(cache)
    
    # নতুন টেস্ট: সিরিজ ডিটেকশন
    print(f"\n🎯 সিরিজ ডিটেকশন টেস্ট:")
    test_titles = [
        "Dhoom 2 2004",
        "Dhoom 3 2013", 
        "Baahubali Part 1",
        "Baahubali 2 The Conclusion",
        "Avatar 2009",
        "Avatar The Way of Water 2022",
        "KGF Chapter 1",
        "KGF Chapter 2",
        "Spider-Man 2002",
        "Spider-Man 2 2004",
        "Avengers Endgame 2019",
        "Avengers Infinity War 2018"
    ]
    
    for title in test_titles:
        base = search_engine.extract_base_title(title)
        part = search_engine.extract_part_number(title)
        print(f"   '{title}' → বেস: '{base}', পার্ট: {part}")
    
    # সব সিরিজ মুভি খুঁজে দেখাবে
    search_engine.find_all_series_movies()
    
    print(f"\n✅ search_engine.py আপডেট সম্পূর্ণ!")