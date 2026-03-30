# config.py - SECURE VERSION (GitHub Safe)
import os

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ .env file loaded")
except:
    print("⚠️ .env file not found, using defaults")

# Helper function
def get_env(key, default=None):
    value = os.getenv(key)
    return value if value is not None else default

# ================== TELEGRAM ==================
BOT_TOKEN = get_env('BOT_TOKEN')
BOT_USERNAME = get_env('BOT_USERNAME')

# ================== ADMIN ==================
ADMIN_USER_IDS = [6723820690]   # এটি সিক্রেট নয়, রাখতে সমস্যা নেই

# অ্যানোনিমাস অ্যাডমিন স্পেশাল আইডি
ANONYMOUS_ADMIN_ID = 1087968824  # টেলিগ্রামের অ্যানোনিমাস অ্যাডমিন আইডি

# ================== BLOGGER ==================
BLOGGER_BLOGS = [
    {
        'name': 'MBBD_Main',
        'blog_id': get_env('BLOGGER_BLOG_ID_1'),
        'api_key': get_env('BLOGGER_API_KEY_1')
    },
    {
        'name': '69 Mxxd',
        'blog_id': get_env('BLOGGER_BLOG_ID_2'),
        'api_key': get_env('BLOGGER_API_KEY_2')
    }
]

# ================== TELEGRAM CHATS ==================
GROUP_ID = get_env('GROUP_ID')
CHANNEL_ID = get_env('CHANNEL_ID')
REQUEST_NOTIFICATION_CHANNEL = get_env('REQUEST_NOTIFICATION_CHANNEL')

# ================== REQUEST SYSTEM ==================
REQUEST_SETTINGS = {
    'max_requests_per_day': int(get_env('MAX_REQUESTS_PER_DAY', 5)),
    'cooldown_hours': 24,
}
REQUEST_FILE = get_env('REQUEST_FILE', 'data/movie_requests.json')
REQUEST_COMMANDS = ['/request', '/req', 'request', 'req']

# ================== URLS ==================
FACEBOOK_GROUP_URL = get_env('FACEBOOK_GROUP_URL')
TELEGRAM_CHANNEL_URL = get_env('TELEGRAM_CHANNEL_URL')
MOVIE_GROUP_URL = get_env('MOVIE_GROUP_URL')

# ================== WEBSITE ==================
WEBSITE_LINKS = {
    'premium': get_env('WEBSITE_PREMIUM'),
    'adult': get_env('WEBSITE_ADULT')
}

# ================== APP SETTINGS ==================
SCRAPING_INTERVAL = 24 * 60 * 60
MAX_RETRIES = 3
CACHE_FILE = get_env('CACHE_FILE', 'data/movies_cache.json')
QNA_FILE = "data/qna.json"
RESPONSE_TIMEOUT = 10
MAX_MESSAGE_LENGTH = 4000
REFRESH_INTERVAL = int(get_env('REFRESH_INTERVAL_MINUTES', 30)) * 60


# ================== AI AGENT ==================
# OpenRouter সরিয়ে Google API যোগ করুন
GOOGLE_API_KEY = get_env('GOOGLE_API_KEY')

# ================== NEW FILES ==================
USER_PROFILES_FILE = get_env('USER_PROFILES_FILE', 'data/user_profiles.json')
LEARNING_CACHE_FILE = get_env('LEARNING_CACHE_FILE', 'data/learning_cache.json')

# ================== RECOMMENDATION ==================
ENABLE_RECOMMENDATIONS = get_env('ENABLE_RECOMMENDATIONS', 'True').lower() == 'true'
TRENDING_LIMIT = int(get_env('TRENDING_LIMIT', 5))
SIMILAR_MOVIES_LIMIT = int(get_env('SIMILAR_MOVIES_LIMIT', 3))

# ================== MESSAGES ==================
DEFAULT_RESPONSE = """
<b>দুঃখিত! 😔 আপনি যে বিষয়ে জানতে চেয়েছেন এর উত্তর আমার কাছে নেই। </b>

<b>আপনাকে কি নতুন কোনো মুভি খুঁজতে সাহায্য করবো?</b>
আপনার পছন্দের মুভি সার্চ করতে নিচের উদাহরণগুলো কপি করুন:

✅ <code>RRR</code>
✅ <code>Pushpa</code>
অথবা,
✅ <code>/search RRR</code>
✅ <code>/search Pushpa</code>

<b>যদি ওপরের দেয়া নিয়মে আপনার কাঙ্খিত মুভিটি না পান তাহলে নিচের দেয়া নিয়মে মুভি রিকোয়েস্ট করুন ।</b>
✅ <code>/req RRR 2023</code>
✅ <code>/req Pushpa 2024</code>

এরপর মুভির নামটি পরিবর্তন করে সেন্ড করুন।
"""

# ================== AUTO RESPONSE SYSTEM (NEW) ==================

# অটো রেসপন্সের জন্য কীওয়ার্ড লিস্ট
AUTO_RESPONSE_KEYWORDS = {
    'website': ['ওয়েবসাইট', 'website', 'সাইট', 'site', 'web', 'ওয়েব', 'লিংক', 'link', 'ডাউনলোড লিংক', 'download link'],
    'facebook': ['ফেসবুক', 'facebook', 'fb', 'ফবি', 'fb group', 'ফেসবুক গ্রুপ'],
    'telegram': ['টেলিগ্রাম', 'telegram', 'tg', 'চ্যানেল', 'channel', 'টেলি', 't.me'],
    'all': ['লিংক দিন', 'link দেন', 'সব লিংক', 'all links', 'গ্রুপ লিংক', 'group link', 'কোথায় পাব', 'kothay pabo', 'যোগ দিবো']
}

# অটো রেসপন্স সেটিংস
AUTO_RESPONSE_SETTINGS = {
    'enabled': True,
    'cooldown_seconds': 30,  # একই ইউজারের জন্য ৩০ সেকেন্ড কুলডাউন
}

# সকল লিংকের সংগ্রহ
SOCIAL_LINKS = {
    'telegram_channel': {
        'name': '📢 টেলিগ্রাম চ্যানেল',
        'url': get_env('TELEGRAM_CHANNEL_URL'),
        'emoji': '📢',
        'description': 'সকল মুভি আপডেট সবার আগে'
    },
    'facebook_group': {
        'name': '📘 ফেসবুক গ্রুপ',
        'url': get_env('FACEBOOK_GROUP_URL'),
        'emoji': '📘',
        'description': 'মুভি আলোচনা ও রিকোয়েস্ট'
    },
    'movie_group': {
        'name': '🎬 মুভি গ্রুপ',
        'url': get_env('MOVIE_GROUP_URL'),
        'emoji': '🎬',
        'description': 'এক্সক্লুসিভ কন্টেন্ট'
    },
    'website': {
        'name': '🌐 প্রিমিয়াম ওয়েবসাইট',
        'url': get_env('WEBSITE_PREMIUM'),
        'emoji': '🌐',
        'description': 'সকল মুভি ডাউনলোড লিংক'
    },
    'adult_website': {
        'name': '🔞 অ্যাডাল্ট জোন (18+)',
        'url': get_env('WEBSITE_ADULT'),
        'emoji': '🔞',
        'description': 'প্রাইভেট কালেকশন'
    }
}

# অটো রেসপন্স মেসেজ টেমপ্লেট
AUTO_RESPONSE_MESSAGE = """
🔗 <b>{user_mention}</b> 👋

আপনার প্রয়োজনীয় লিংকগুলো নিচে দেওয়া হলো:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 <b>আমাদের সাথে যুক্ত হন:</b>

• <b>📢 টেলিগ্রাম চ্যানেল</b> → সর্বশেষ আপডেট পেতে
• <b>📘 ফেসবুক গ্রুপ</b> → মুভি আলোচনা ও রিকোয়েস্ট করতে  
• <b>🎬 মুভি গ্রুপ</b> → এক্সক্লুসিভ কন্টেন্ট পেতে
• <b>🌐 ওয়েবসাইট</b> → সরাসরি ডাউনলোড লিংক পেতে

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 <b>সহজ উপায়:</b> নিচের বাটনে ক্লিক করুন 👇
"""

BAN_MESSAGE = """
🚫 <b> স্প্যামার ডিটেক্টেড!</b>

❌ ইউজার: {user_name} (ID: {user_id})
📛 কারণ: লিংক শেয়ার করা
⏰ সময়: {ban_time}

⚠️ <b>গ্রুপ রুলস ভঙ্গ করায় ইউজারকে মিউট করা হয়েছে</b>

📜 <b>গ্রুপ নিয়ম:</b>
• শুধুমাত্র এডমিনরা লিংক শেয়ার করতে পারবেন
• সাধারণ মেম্বাররা লিংক শেয়ার করলে মিউট
• কোনো ধরনের স্প্যাম করা নিষিদ্ধ

🔒 <b>লিংক শেয়ার করার অনুমতি শুধু এডমিনদের জন্য!</b>
"""

# ================== MESSAGE FILTERING ==================
BLACKLISTED_MESSAGES = [
    # শুধু স্প্যাম ও লিংক
    'http://', 'https://', 'www.', '.com', '.net', '.org', '.bd',
    't.me/', 'telegram.me/', 'bit.ly', 'tinyurl', 'goo.gl',
    
    # স্ক্যাম কীওয়ার্ড
    'টাকা', 'লোন', 'বোনাস', 'ক্যাসিনো', 'জুয়া',
    'sex', 'porn', 'xxx', 'adult', '18+',
    
    # অশ্লীল ভাষা (আপনার গ্রুপের নিয়ম অনুযায়ী)
]

GREETINGS_KEYWORDS = [
    # বাংলা গ্রিটিংস
    'হাই', 'হ্যালো', 'হেলো', 'আসসালামু আলাইকুম', 'সালাম', 'নমস্কার', 'প্রণাম',
    'কেমন আছেন', 'কেমন আছো', 'কি খবর', 'কি অবস্থা', 'সব ভালো',
    'শুভ সকাল', 'শুভ দুপুর', 'শুভ বিকাল', 'শুভ রাত্রি',
    'ভাই কেমন আছ', 'আপনা কেমন আছেন', 'ওয়াসালাম',
    
    # ইংলিশ গ্রিটিংস
    'hi', 'hello', 'hey', 'hlw', 'hey there', 'hola', 'yo',
    'whats up', 'sup', 'howdy', 'how are you', 'how is it going',
    'good morning', 'good afternoon', 'good evening', 'good night',
    'whats new', 'long time no see',
    
    # ধন্যবাদ
    'ধন্যবাদ', 'থ্যাংকস', 'thanks', 'thank you', 'অনেক ধন্যবাদ',
    
    # হেল্প/সাহায্য
    'বট কাজ করছে না', 'help', 'সাহায্য', 'please help', 
    'কি করে', 'কিভাবে', 'how to', 'help me', 'সাপোর্ট',
    
    # ইমোজি ও ছোট প্রতিক্রিয়া
    '😂', '🔥', '❤️', '👍', '👎', '🙏', '🥰', '😭',
    '?', '???', '!!!!'
]

MOVIE_PATTERNS = [
    r'^[a-zA-Z0-9\s]{2,25}$',
    r'^[\u0980-\u09FF\s]{2,15}$',
    r'.*\b(19|20)\d{2}\b',
    r'.*\b(part|chapter|season|episode)\b',
]

print("✅ Secure Config Loaded Successfully")
