# interactive_buttons.py - ইন্টারেক্টিভ বাটন সিস্টেম
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def create_confirmation_keyboard(suggested_movie, original_query):
    """স্পেলিং করেকশনের জন্য কনফার্মেশন বাটন তৈরি করবে"""
    keyboard = [
        [
            InlineKeyboardButton(
                "✅ হ্যাঁ, এই মুভিটি", 
                callback_data=f"confirm_{suggested_movie['title']}"
            ),
            InlineKeyboardButton(
                "❌ না, অন্য মুভি", 
                callback_data=f"deny_{original_query}"
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_movie_results_keyboard(movies):
    """মুভি রেজাল্টের জন্য বাটন তৈরি করবে"""
    keyboard = []
    for movie in movies:
        button_text = f"🎬 {movie['title']}"
        if movie.get('year'):
            button_text += f" ({movie['year']})"
        
        keyboard.append([
            InlineKeyboardButton(button_text, url=movie['link'])
        ])
    
    return InlineKeyboardMarkup(keyboard)

def create_series_keyboard(series_movies):
    """একই সিরিজের মুভিগুলোর জন্য বাটন তৈরি করবে"""
    keyboard = []
    
    for movie in series_movies:
        quality_text = f" - {movie['quality']}" if movie.get('quality') else ""
        button_text = f"📀 {movie['title']}{quality_text}"
        
        keyboard.append([
            InlineKeyboardButton(button_text, url=movie['link'])
        ])
    
    # সাহায্যের জন্য বাটন
    keyboard.append([
        InlineKeyboardButton("🆘 সাহায্য চাই", callback_data="help_search")
    ])
    
    return InlineKeyboardMarkup(keyboard)

def create_search_suggestions_keyboard(suggestions):
    """সার্চ সাজেশন বাটন তৈরি করবে"""
    keyboard = []
    
    for i, movie in enumerate(suggestions[:3], 1):  # সর্বোচ্চ ৩টি সাজেশন
        keyboard.append([
            InlineKeyboardButton(
                f"🎯 {i}. {movie['title']}", 
                callback_data=f"suggest_{movie['title']}"
            )
        ])
    
    return InlineKeyboardMarkup(keyboard)

# টেস্ট করার জন্য
if __name__ == "__main__":
    # ডেমো ডাটা দিয়ে টেস্ট
    demo_movie = {
        'title': 'Avengers Endgame',
        'year': '2019',
        'quality': '1080p',
        'link': 'https://example.com/avengers-endgame'
    }
    
    demo_movies = [
        {
            'title': 'Dhoom',
            'year': '2004',
            'quality': '720p',
            'link': 'https://example.com/dhoom'
        },
        {
            'title': 'Dhoom 2', 
            'year': '2006',
            'quality': '1080p',
            'link': 'https://example.com/dhoom-2'
        },
        {
            'title': 'Dhoom 3',
            'year': '2013',
            'quality': '4K',
            'link': 'https://example.com/dhoom-3'
        }
    ]
    
    print("🧪 বাটন সিস্টেম টেস্ট:")
    
    # ১. কনফার্মেশন বাটন টেস্ট
    confirm_keyboard = create_confirmation_keyboard(demo_movie, "avenger")
    print("✅ কনফার্মেশন বাটন তৈরি হয়েছে")
    
    # ২. মুভি রেজাল্ট বাটন টেস্ট  
    results_keyboard = create_movie_results_keyboard([demo_movie])
    print("✅ মুভি রেজাল্ট বাটন তৈরি হয়েছে")
    
    # ৩. সিরিজ বাটন টেস্ট
    series_keyboard = create_series_keyboard(demo_movies)
    print("✅ সিরিজ বাটন তৈরি হয়েছে")
    
    # ৪. সাজেশন বাটন টেস্ট
    suggestions_keyboard = create_search_suggestions_keyboard(demo_movies)
    print("✅ সাজেশন বাটন তৈরি হয়েছে")
    
    print("\n🎯 সব বাটন সিস্টেম সফলভাবে তৈরি হয়েছে!")


# ================== SOCIAL LINKS BUTTONS (NEW) ==================

def create_social_links_keyboard():
    """সোশ্যাল লিংকের জন্য সুন্দর বাটন তৈরি করবে"""
    from config import SOCIAL_LINKS
    
    keyboard = []
    
    # টেলিগ্রাম চ্যানেল
    if SOCIAL_LINKS['telegram_channel']['url'] and SOCIAL_LINKS['telegram_channel']['url'] != '#':
        keyboard.append([
            InlineKeyboardButton(
                f"📢 {SOCIAL_LINKS['telegram_channel']['name']}", 
                url=SOCIAL_LINKS['telegram_channel']['url']
            )
        ])
    
    # ফেসবুক গ্রুপ
    if SOCIAL_LINKS['facebook_group']['url'] and SOCIAL_LINKS['facebook_group']['url'] != '#':
        keyboard.append([
            InlineKeyboardButton(
                f"📘 {SOCIAL_LINKS['facebook_group']['name']}", 
                url=SOCIAL_LINKS['facebook_group']['url']
            )
        ])
    
    # মুভি গ্রুপ
    if SOCIAL_LINKS['movie_group']['url'] and SOCIAL_LINKS['movie_group']['url'] != '#':
        keyboard.append([
            InlineKeyboardButton(
                f"🎬 {SOCIAL_LINKS['movie_group']['name']}", 
                url=SOCIAL_LINKS['movie_group']['url']
            )
        ])
    
    # ওয়েবসাইট
    if SOCIAL_LINKS['website']['url'] and SOCIAL_LINKS['website']['url'] != '#':
        keyboard.append([
            InlineKeyboardButton(
                f"🌐 {SOCIAL_LINKS['website']['name']}", 
                url=SOCIAL_LINKS['website']['url']
            )
        ])
    
    # অ্যাডাল্ট ওয়েবসাইট (যদি থাকে)
    if SOCIAL_LINKS.get('adult_website', {}).get('url') and SOCIAL_LINKS['adult_website']['url'] != '#':
        keyboard.append([
            InlineKeyboardButton(
                f"🔞 {SOCIAL_LINKS['adult_website']['name']}", 
                url=SOCIAL_LINKS['adult_website']['url']
            )
        ])
    
    return InlineKeyboardMarkup(keyboard)