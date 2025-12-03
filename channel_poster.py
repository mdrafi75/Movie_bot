# channel_poster.py - স্মার্ট আপডেট সিস্টেম সহ
from telegram import InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
import config

class ChannelPoster:
    def __init__(self, cache_manager):
        self.channel_id = config.CHANNEL_ID
        self.cache_manager = cache_manager
        self.posted_movies = {}  # {message_id: movie_data}
    
    def create_download_button(self, movie):
        """লিংক স্ট্যাটাস অনুযায়ী বাটন তৈরি করবে"""
        detail_link = movie.get('detail_link')
        blogger_url = movie.get('blogger_url', '#')
        
        if detail_link:
            # লিংক থাকলে ডাউনলোড বাটন
            return InlineKeyboardMarkup([
                [InlineKeyboardButton("📥 ডাউনলোড লিংক", url=detail_link)]
            ])
        else:
            # লিংক না থাকলে অপেক্ষমান বাটন
            return InlineKeyboardMarkup([
                [InlineKeyboardButton("⏳ লিংক খুব শীঘ্রই আসছে...", callback_data="link_coming_soon")]
            ])
    
    async def post_movie_to_channel(self, movie, bot):
        """চ্যানেলে মুভি পোস্ট করবে - স্মার্ট সিস্টেম"""
        try:
            title = movie.get('title', 'Unknown Title')
            rating = movie.get('rating', 'N/A')
            quality = movie.get('quality', 'HD')
            year = movie.get('year', 'N/A')
            image_url = movie.get('image_url')
            
            # ক্যাপশন তৈরি
            if movie.get('detail_link'):
                caption = f"""
🎬 <b>{title}</b>

⭐ <b>রেটিং:</b> {rating}
📀 <b>কোয়ালিটি:</b> {quality}  
🕒 <b>সাল:</b> {year}

👇 <b>ডাউনলোড করতে নিচের বাটনে ক্লিক করুন</b>


"""
            else:
                caption = f"""
🎬 <b>{title}</b>

⭐ <b>রেটিং:</b> {rating}
📀 <b>কোয়ালিটি:</b> {quality}  
🕒 <b>সাল:</b> {year}

⚠️ <b>লিংক খুব দ্রুত অ্যাড করা হবে</b>
<b>অনুগ্রহ করে অপেক্ষা করুন...</b>


"""
            
            # বাটন তৈরি
            keyboard = self.create_download_button(movie)
            
            # পোস্ট করবে
            if image_url:
                message = await bot.send_photo(
                    chat_id=self.channel_id,
                    photo=image_url,
                    caption=caption,
                    parse_mode='HTML',
                    reply_markup=keyboard
                )
            else:
                message = await bot.send_message(
                    chat_id=self.channel_id,
                    text=caption,
                    parse_mode='HTML',
                    reply_markup=keyboard
                )
            
            # মেসেজ আইডি সেভ করবে পরবর্তী আপডেটের জন্য
            self.posted_movies[message.message_id] = {
                'movie_title': title,
                'has_link': bool(movie.get('detail_link'))
            }
            
            print(f"✅ চ্যানেলে পোস্ট করা হয়েছে: {title} (লিংক: {'✅' if movie.get('detail_link') else '⏳'})")
            return True
            
        except Exception as e:
            print(f"❌ চ্যানেলে পোস্ট করতে সমস্যা: {e}")
            return False
    
    async def update_movie_post(self, movie_title, bot):
        """মুভি পোস্ট আপডেট করবে যখন লিংক পাওয়া যাবে"""
        try:
            # কোন মেসেজে এই মুভি আছে খুঁজবে
            target_message_id = None
            for msg_id, movie_data in self.posted_movies.items():
                if movie_data['movie_title'] == movie_title and not movie_data['has_link']:
                    target_message_id = msg_id
                    break
            
            if target_message_id:
                # ক্যাশে থেকে আপডেটেড মুভি ডাটা নিবে
                movie = self.cache_manager.get_movie_by_title(movie_title)
                if movie and movie.get('detail_link'):
                    # নতুন ক্যাপশন এবং বাটন তৈরি
                    caption = f"""
🎬 <b>{movie_title}</b>

⭐ <b>রেটিং:</b> {movie.get('rating', 'N/A')}
📀 <b>কোয়ালিটি:</b> {movie.get('quality', 'HD')}  
🕒 <b>সাল:</b> {movie.get('year', 'N/A')}

👇 <b>ডাউনলোড করতে নিচের বাটনে ক্লিক করুন</b>


"""
                    keyboard = self.create_download_button(movie)
                    
                    # মেসেজ এডিট করবে
                    await bot.edit_message_caption(
                        chat_id=self.channel_id,
                        message_id=target_message_id,
                        caption=caption,
                        reply_markup=keyboard,
                        parse_mode='HTML'
                    )
                    
                    # স্ট্যাটাস আপডেট করবে
                    self.posted_movies[target_message_id]['has_link'] = True
                    print(f"✅ চ্যানেল পোস্ট আপডেট হয়েছে: {movie_title}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ পোস্ট আপডেট করতে সমস্যা: {e}")
            return False

    async def post_multiple_movies(self, movies, bot):
        """একাধিক মুভি চ্যানেলে পোস্ট করবে"""
        success_count = 0
        for movie in movies:
            success = await self.post_movie_to_channel(movie, bot)
            if success:
                success_count += 1
        return success_count