

import sys
from blogger_api import BloggerAPI
from cache_manager import CacheManager
from scraper import MovieScraper
from search_engine import SearchEngine
from interactive_buttons import (
    create_confirmation_keyboard, 
    create_movie_results_keyboard,
    create_series_keyboard,
    create_search_suggestions_keyboard
)
import re
from request_manager import RequestManager
from admin_notifier import AdminNotifier
from channel_poster import ChannelPoster
from telegram.ext import ChatMemberHandler
from message_classifier import MessageClassifier
from auto_refresher import AutoRefresher
from telegram import ChatPermissions
from datetime import datetime
import threading
import time
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from short_admin_menu import ShortAdminMenu
from local_ai_agent import LocalAIAgent
from user_profile import UserProfileManager
from learning_system import LearningSystem
from context_memory import ContextMemory
from recommendation_engine import RecommendationEngine
import aiohttp
import json
# অটো রেসপন্সের জন্য ইমপোর্ট
from interactive_buttons import create_social_links_keyboard
from datetime import datetime

# আমাদের কনফিগারেশন ইম্পোর্ট
import config
# bot.py - প্রথম ১০ লাইনের মধ্যে এই কোড যোগ করুন
import os
from flask import Flask, request
from threading import Thread

# ✅ Render-এর জন্য সঠিক পোর্ট
PORT = int(os.environ.get('PORT', 10000))

# ✅ Flask app তৈরি
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "🎬 Movie Bot is Running! | Status: ACTIVE ✅"

@flask_app.route('/health')
def health():
    return "OK", 200

@flask_app.route('/ping')
def ping():
    return "PONG", 200

# ✅ Flask server চালু করব আলাদা থ্রেডে
def run_flask():
    flask_app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)

# ✅ Thread শুরু করব
flask_thread = Thread(target=run_flask, daemon=True)
flask_thread.start()
print(f"✅ Flask server started on port {PORT}")

# লগিং সেটআপ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# গ্রিটিংস এর লিস্ট (বাংলা এবং ইংলিশ)
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
    'whats new', 'long time no see'
]

# ওয়েলকাম মেসেজ (নতুন ইউজার গ্রুপে জয়েন করলে)
WELCOME_MESSAGE = """
<b>🎬 স্বাগতম {user_mention}!</b>

<b>✨ আমাদের মুভি কমিউনিটিতে আপনাকে স্বাগতম!</b>

📌 <b>গ্রুপ রুলস:</b>
• শুধু মুভি সম্পর্কিত আলোচনা
• কোনো স্প্যাম/লিংক শেয়ার নিষিদ্ধ
• নিয়ম ভঙ্গ করলে সরাসরি রিমুভ

🚀 <b>আমাদের অফিসিয়াল গ্রুপ:</b>
• সর্বশেষ মুভি আপডেট
• এক্সক্লুসিভ কন্টেন্ট  
• মুভি রিকুয়েস্ট

<b>👇 নিচের বাটনে ক্লিক করে জয়েন করুন</b>
"""

# গ্রিটিংস রেসপন্স মেসেজ (হাই/হ্যালো দিলে)
GREETING_RESPONSE_MESSAGE = """
<b>🎬 Hey! {user_mention} মুভি লাভার! </b>

<b>গ্রুপে মেসেজ করার জন্য আপনাকে ধন্যবাদ! 🎉 </b>
আপনি কি নতুন কোনো মুভি খুঁজছেন? যদি মুভি প্রয়োজন হয় এখন ই সার্চ করুন নিচের দেয়া নিয়মে 

<b>সরাসরি সঠিক মুভির নাম লিখুন</b>
<code> Diesel </code>   <code> Kaantha </code>
অথবা,
<code>/search মুভির_নাম </code>
<code>/search Kaantha </code>
<b>সঠিক মুভির নাম লিখুন গ্রুপে</b>
"""

# ইনলাইন কীবোর্ড তৈরি
def create_welcome_keyboard():
    """ওয়েবকাম মেসেজের জন্য ইনলাইন বাটন তৈরি"""
    keyboard = [
        [
            InlineKeyboardButton("📘 ফেসবুক গ্রুপ", url=config.FACEBOOK_GROUP_URL),
            InlineKeyboardButton("📢 টেলিগ্রাম চ্যানেল", url=config.TELEGRAM_CHANNEL_URL)
        ],
        [
            InlineKeyboardButton("🎬 মুভি গ্রুপ", url=config.MOVIE_GROUP_URL),
            InlineKeyboardButton("🆘 সাহায্য", callback_data="help")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# গ্রিটিংস ডিটেক্ট ফাংশন
def is_greeting_message(message_text):
    """মেসেজটি গ্রিটিংস কিনা চেক করবে - CORRECTED VERSION"""
    if not message_text:
        return False
        
    message_lower = message_text.lower().strip()
    
    # শুধু এক্সাক্ট গ্রিটিংস লিস্ট
    exact_greetings = [
        # English greetings
        'hi', 'hello', 'hey', 'hlw', 'hey there', 'hola', 'yo',
        'whats up', 'sup', 'howdy', 'how are you', 'how is it going',
        'good morning', 'good afternoon', 'good evening', 'good night',
        'whats new', 'long time no see', 'wassup',
        
        # Bengali greetings
        'হাই', 'হ্যালো', 'হেলো', 'আসসালামু আলাইকুম', 'সালাম', 'নমস্কার', 'প্রণাম',
        'কেমন আছেন', 'কেমন আছো', 'কি খবর', 'কি অবস্থা', 'সব ভালো',
        'শুভ সকাল', 'শুভ দুপুর', 'শুভ বিকাল', 'শুভ রাত্রি',
        'ভাই কেমন আছ', 'আপনা কেমন আছেন', 'ওয়াসালাম',
    ]
    
    # ১. প্রথমে এক্সাক্ট ম্যাচ চেক
    for greeting in exact_greetings:
        if greeting == message_lower:
            print(f"✅ গ্রিটিংস এক্সাক্ট ম্যাচ: '{greeting}'")
            return True
    
    # ২. মেসেজের শব্দগুলো
    message_words = message_lower.split()
    
    # ৩. শুধু ছোট মেসেজের জন্য (২ শব্দ বা কম)
    if len(message_words) <= 2:
        for greeting in exact_greetings:
            greeting_words = greeting.split()
            
            # যদি মেসেজের কোনো শব্দ গ্রিটিংসের সম্পূর্ণ শব্দের সাথে মেলে
            for msg_word in message_words:
                for greet_word in greeting_words:
                    if msg_word == greet_word:
                        print(f"✅ গ্রিটিংস শব্দ ম্যাচ: '{msg_word}' in '{greeting}'")
                        return True
    
    print(f"❌ গ্রিটিংস না: '{message_text}'")
    return False

# গ্রিটিংস রেসপন্স হ্যান্ডলার
async def handle_greeting_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """গ্রিটিংস মেসেজের রেসপন্স দিবে"""
    user = update.message.from_user
    user_mention = f"@{user.username}" if user.username else user.first_name
    
    # ইউজারকে মেনশন সহ গ্রিটিংস রেসপন্স মেসেজ
    response_text = GREETING_RESPONSE_MESSAGE.format(user_mention=user_mention)
    
    await update.message.reply_text(
        text=response_text,
        reply_markup=create_welcome_keyboard(),
        parse_mode='HTML',  # Markdown থেকে HTML-এ পরিবর্তন
        reply_to_message_id=update.message.message_id
    )
    
    print(f"👋 গ্রিটিংস রেসপন্স দিলাম: {user.first_name} - '{update.message.text}'")


async def bulk_post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """সব মুভি নতুন চ্যানেলে পোস্ট করার কমান্ড (শুধু এডমিন)"""
    user = update.message.from_user
    
    if user.id not in config.ADMIN_USER_IDS:
        await update.message.reply_text("⛔ শুধুমাত্র এডমিন এই কমান্ড ব্যবহার করতে পারেন।")
        return
    
    start_from = 0
    limit = None
    reverse = False  # ✅ ডিফল্ট False
    
    if context.args:
        try:
            if len(context.args) >= 1:
                start_from = int(context.args[0])
            if len(context.args) >= 2:
                limit = int(context.args[1])
            if len(context.args) >= 3 and context.args[2].lower() == 'reverse':
                reverse = True
        except:
            pass
    
    total_movies = cache_manager.get_movie_count()
    
    reverse_text = "✅ (নতুন শেষে)" if reverse else "❌ (নতুন শুরুতে)"
    
    confirm_msg = f"""
⚠️ <b>বাল্ক পোস্টিং শুরু করতে যাচ্ছেন!</b>

📊 <b>মোট মুভি:</b> {total_movies} টি
📢 <b>চ্যানেল:</b> {config.CHANNEL_ID}
🔄 <b>পোস্ট শুরু:</b> {start_from} নম্বর থেকে
📦 <b>লিমিট:</b> {limit if limit else 'সব'}
🔄 <b>অর্ডার:</b> {reverse_text}

⏱️ <b>সময় লাগবে:</b> প্রায় {((limit if limit else total_movies) * 2) // 60} মিনিট

✅ <b>পোস্ট শুরু করতে:</b> /confirm_bulk_post
❌ <b>বাতিল করতে:</b> /cancel
"""
    
    context.user_data['bulk_post_pending'] = {
        'start_from': start_from,
        'limit': limit,
        'reverse': reverse
    }
    
    await update.message.reply_text(confirm_msg, parse_mode='HTML')


async def confirm_bulk_post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """বাল্ক পোস্টিং কনফার্ম করার কমান্ড"""
    user = update.message.from_user
    
    if user.id not in config.ADMIN_USER_IDS:
        return
    
    if 'bulk_post_pending' not in context.user_data:
        await update.message.reply_text("❌ কোনো pending পোস্ট নেই। প্রথমে /bulk_post দিয়ে শুরু করুন।")
        return
    
    pending = context.user_data['bulk_post_pending']
    start_from = pending['start_from']
    limit = pending['limit']
    reverse = pending.get('reverse', False)
    
    reverse_text = "নতুন শেষে" if reverse else "নতুন শুরুতে"
    
    await update.message.reply_text(
        f"🔄 পোস্ট শুরু হচ্ছে...\n\n"
        f"📦 অর্ডার: {reverse_text}\n"
        f"📊 মুভি সংখ্যা: {limit if limit else cache_manager.get_movie_count()} টি\n"
        f"⏱️ দয়া করে অপেক্ষা করুন..."
    )
    
    try:
        from channel_poster import ChannelPoster
        channel_poster = ChannelPoster(cache_manager)
        
        # ✅ রিভার্স প্যারামিটার পাস করছি
        success, message = await channel_poster.post_all_movies_to_channel(
            bot=context.bot,
            start_from=start_from,
            limit=limit,
            reverse_order=reverse
        )
        
        await update.message.reply_text(
            f"✅ <b>বাল্ক পোস্টিং সম্পূর্ণ!</b>\n\n"
            f"📊 <b>ফলাফল:</b> {message}\n"
            f"📢 <b>চ্যানেল:</b> {config.CHANNEL_ID}\n\n"
            f"🔄 অর্ডার: {reverse_text}",
            parse_mode='HTML'
        )
        
        del context.user_data['bulk_post_pending']
        
    except Exception as e:
        await update.message.reply_text(f"❌ পোস্টিং এরর: {e}")


async def cancel_bulk_post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """বাল্ক পোস্টিং বাতিল করার কমান্ড"""
    user = update.message.from_user
    
    if user.id not in config.ADMIN_USER_IDS:
        return
    
    if 'bulk_post_pending' in context.user_data:
        del context.user_data['bulk_post_pending']
        await update.message.reply_text("✅ বাল্ক পোস্টিং বাতিল করা হয়েছে।")
    else:
        await update.message.reply_text("❌ কোনো pending পোস্ট নেই।")

# সব মেসেজ হ্যান্ডলার

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """আপডেটেড মেসেজ হ্যান্ডলার - অটো রেসপন্স কীওয়ার্ড সহ"""
    user_message = update.message.text
    user = update.effective_user
    user_id = user.id
    chat_type = update.effective_chat.type
    
    print(f"\n📨 মেসেজ: '{user_message[:50]}...' from {user.first_name} in {chat_type}")
    
    # ========== নতুন: অটো রেসপন্স কীওয়ার্ড চেক ==========
    if chat_type in ['group', 'supergroup'] and config.AUTO_RESPONSE_SETTINGS.get('enabled', True):
        if check_auto_response_keywords(user_message):
            # কুলডাউন চেক
            if is_cooldown_active(user_id):
                print(f"⏰ কুলডাউন সক্রিয়: {user_id}, রেসপন্স দিচ্ছি না")
            else:
                # ইউজার মেনশন তৈরি
                user_mention = f"@{user.username}" if user.username else user.first_name
                
                # মেসেজ তৈরি
                response_text = config.AUTO_RESPONSE_MESSAGE.format(user_mention=user_mention)
                
                # বাটন তৈরি
                reply_markup = create_social_links_keyboard()
                
                # মেসেজ পাঠানো
                await update.message.reply_text(
                    text=response_text,
                    reply_markup=reply_markup,
                    parse_mode='HTML',
                    disable_web_page_preview=True,
                    reply_to_message_id=update.message.message_id
                )
                
                # কুলডাউন আপডেট
                update_cooldown(user_id)
                print(f"✅ অটো রেসপন্স পাঠানো হয়েছে: {user_id}")
                return  # এখান থেকে রিটার্ন, নিচের কোড আর এক্সিকিউট হবে না
    
    # ১. গ্রুপে লিংক চেক (স্প্যাম প্রটেকশন) - শুধু সাধারণ মেম্বারদের জন্য
    if chat_type in ['group', 'supergroup']:
        if contains_any_link(user_message or ""):
            # এডমিন চেক - খুব সাবধানে করব
            is_admin = await is_user_admin(update, context)
            
            if is_admin:
                # এডমিন হলে কিছু করব না, মেসেজ থাকবে
                print(f"👑 এডমিনের লিংক মেসেজ: {user_message[:50]}... (কোনো অ্যাকশন নেই)")
                return  # এখান থেকে রিটার্ন, নিচের কোনো কোড এক্সিকিউট হবে না
            
            # এডমিন না হলে (সাধারণ মেম্বার) → মিউট করব
            print(f"🚫 সাধারণ মেম্বারের লিংক ডিটেক্ট: {user_id}")
            await mute_user_permanently(update, context)
            return
        

        # ========== ডাউনলোড গাইড চেক (AI Agent দিয়ে) ==========
        if local_ai_agent:
            try:
                intent_data = await local_ai_agent.detect_intent(user_message, user_id)
                if intent_data and intent_data.get('intent') == 'download_guide' and intent_data.get('confidence', 0) > 0.7:
                    user_mention = f"@{user.username}" if user.username else user.first_name
                    
                    # ১. ভিডিও পোস্টটি ফরওয়ার্ড করব
                    try:
                        await context.bot.forward_message(
                            chat_id=update.effective_chat.id,
                            from_chat_id='mbbdhelp',  # চ্যানেলের ইউজারনাম
                            message_id=2,  # পোস্ট নম্বর
                            reply_to_message_id=update.message.message_id
                        )
                        print(f"✅ ডাউনলোড গাইড ভিডিও ফরওয়ার্ড করা হয়েছে: {user_id}")
                    except Exception as e:
                        print(f"❌ ফরওয়ার্ড করতে সমস্যা: {e}")
                        # ফরওয়ার্ড ব্যর্থ হলে লিংক আকারে পাঠাব
                        await update.message.reply_text(
                            f"🎬 {user_mention} 👋\n\n"
                            f"ডাউনলোড গাইড ভিডিও লিংক:\n{config.DOWNLOAD_GUIDE_LINK}\n\n"
                            f"💡 লিংকে ক্লিক করে ভিডিওটি দেখুন।",
                            parse_mode='HTML',
                            reply_to_message_id=update.message.message_id
                        )
                        return
                    
                    # ২. ফরওয়ার্ড করার পর মেনশন সহ টেক্সট মেসেজ
                    await update.message.reply_text(
                        f"🎬 <b>{user_mention}</b> 👋\n\n"
                        f"👆 উপরের ভিডিওটি দেখুন, স্টেপ বাই স্টেপ ফলো করুন।\n\n"
                        f"💡 <b>টিপস:</b>\n"
                        f"• ভিডিও পজ করে ধাপগুলো বুঝে নিন\n"
                        f"• কোনো সমস্যা হলে এডমিনকে জানান",
                        parse_mode='HTML',
                        reply_to_message_id=update.message.message_id
                    )
                    
                    print(f"✅ ডাউনলোড গাইড পাঠানো হয়েছে: {user_id}")
                    return
            except Exception as e:
                print(f"⚠️ ডাউনলোড গাইড চেক এরর: {e}")
    
    # ২. মেসেজ ক্লাসিফাই করুন (ইম্প্রুভড ক্লাসিফায়ার ব্যবহার)
    classifier_result = await message_classifier.classify(
        text=user_message,
        user_id=user_id,
        chat_type=chat_type
    )
    
    intent = classifier_result['intent']
    confidence = classifier_result['confidence']
    reason = classifier_result['reason']
    
    print(f"🧠 Classifier: intent={intent}, confidence={confidence:.2f}, reason={reason}")
    
    # ৩. কনফিডেন্স চেক - কম আত্মবিশ্বাসে চুপ থাকুন
    MIN_CONFIDENCE = 0.7  # ৭০% এর নিচে রেসপন্স দেবেন না
    
    if confidence < MIN_CONFIDENCE and chat_type != 'private':
        print(f"🤐 Low confidence ({confidence}), staying silent")
        return
    
    # ৪. ইন্টেন্ট অনুযায়ী অ্যাকশন
    if intent == 'COMMAND':
        # কমান্ড অন্য হ্যান্ডলার handle করবে
        return
    
    elif intent == 'GREETING':
        user_mention = f"@{user.username}" if user.username else user.first_name
        greeting_text = f"""👋 {user_mention}! আমি একটি মুভি ফাইন্ডার বট।
মুভি খুঁজতে শুধু নাম লিখুন (যেমন: <code>Diesel</code>)
অথবা /search কমান্ড ব্যবহার করুন।"""
        
        await update.message.reply_text(
            text=greeting_text,
            parse_mode='HTML',
            reply_to_message_id=update.message.message_id
        )
        return
    
    elif intent == 'QUESTION':
        await update.message.reply_text(
            "❓ আমি শুধু মুভি সম্পর্কিত তথ্য দিতে পারি।\nমুভির নাম লিখলে ডাউনলোড লিংক দেব।",
            reply_to_message_id=update.message.message_id
        )
        return
    
    elif intent == 'THANKS':
        await update.message.reply_text(
            "😊 আপনাকে ধন্যবাদ! মুভি লাগলে জানাবেন।",
            reply_to_message_id=update.message.message_id
        )
        return
    
    elif intent == 'MOVIE_QUERY':
        query = classifier_result.get('movie_name', user_message)
        await handle_movie_search(update, context, query)
        return
    
    elif intent == 'MOVIE_REQUEST':
        query = classifier_result.get('movie_name', user_message)
        if len(query.strip()) < 2:
            await send_trending_movies_cards(update, context)
        else:
            context.args = [query]
            await request_command(update, context)
        return
    
    elif intent == 'SPAM' or intent == 'BLACKLISTED':
        # স্প্যাম/ব্ল্যাকলিস্টেড মেসেজ - চুপ থাকুন
        return
    
    else:  # UNKNOWN
        # অজানা মেসেজ - শুধু প্রাইভেট চ্যাটে রেসপন্স দিন
        if chat_type == 'private':
            await update.message.reply_text(
                "🤔 আমি বুঝতে পারিনি। মুভির নাম লিখুন অথবা /help দেখুন।"
            )
        return


# নতুন ফাংশন যোগ করুন - handle_movie_search
async def handle_movie_search(update: Update, context: ContextTypes.DEFAULT_TYPE, query: str):
    """মুভি সার্চ হ্যান্ডলার"""
    user = update.effective_user
    user_id = user.id
    chat_type = update.effective_chat.type
    
    print(f"🔍 Searching for: '{query}'")
    
    if not local_ai_agent:
        await update.message.reply_text("❌ সার্চ সিস্টেম প্রস্তুত নয়।")
        return
    
    results = local_ai_agent.search_movies(query)
    
    if results:
        # মুভি পাওয়া গেলে রেজাল্ট দেখান
        top_score = results[0]['score']
        top_movie = results[0]['movie']
        
        if user_profile_manager:
            user_profile_manager.update_from_search(user_id, top_movie)
        
        if top_score >= 85:
            series_movies = search_engine.get_movie_series(top_movie['title'])
            if series_movies and len(series_movies) > 1:
                for movie in series_movies:
                    await send_movie_result_with_image(update, movie)
            else:
                await send_movie_result_with_image(update, top_movie)
            
            if learning_system and query.lower() != top_movie['title'].lower():
                learning_system.learn_spelling(query, top_movie['title'])
        else:
            movies_to_show = [item['movie'] for item in results[:3]]
            await send_multiple_movie_cards(update, movies_to_show)
            await ask_confirmation_after_cards(update, query, results[:3])
    else:
        # **৬ নম্বর সমস্যার সমাধান: মুভি না পেলে হেল্পফুল মেসেজ**
        user_name = update.effective_user.first_name
        mention = f"@{update.effective_user.username}" if update.effective_user.username else user_name
        
        help_message = f"""
😔 **{mention}**, '{query}' নামে কোনো মুভি খুঁজে পাইনি।

📌 **কেন এমন হতে পারে:**
• বানান ভুল হয়েছে (যেমন: Parasakthi → {query})
• মুভিটি এখনও আমাদের ডাটাবেজে যোগ হয়নি
• শুধু পার্ট/সিরিজ নাম লিখেছেন (মূল নাম না)

💡 **পরামর্শ:**
✅ সঠিক বানান দিয়ে আবার সার্চ করুন
✅ ইংরেজিতে লিখুন (বাংলা অক্ষরে না)
✅ শুধু মুভির মূল নাম লিখুন (যেমন: Parasakthi)
✅ বছর বাদ দিন (যেমন: Parasakthi 2026 → Parasakthi)

📝 **রিকোয়েস্ট করতে:**
<code>/req {query}</code>

👆 উপরের কমান্ডটি কপি করে সেন্ড করুন, এডমিন দেখবেন।
"""
        
        await update.message.reply_text(
            help_message,
            parse_mode='Markdown',
            reply_to_message_id=update.message.message_id
        )
        

async def send_low_confidence_message(update: Update, original_query):
    """খুবই কম স্কোর হলে ইউজারকে সঠিক নাম দিয়ে সার্চ করতে বলে"""
    user = update.effective_user
    user_mention = f"@{user.username}" if user.username else user.first_name
    
    message = f"""
🤔 <b>{user_mention}</b>, আপনি কি '<b>{original_query}</b>' সঠিক লিখেছেন?

আমি এই নামের কাছাকাছি কোনো মুভি খুঁজে পাইনি।

📝 <b>সঠিকভাবে লিখুন:</b>
• শুধু মুভির মূল নাম (যেমন: <code>Diesel</code>)
• ইংরেজিতে লিখুন (বাংলা অক্ষরে না)
• বানান চেক করুন

✅ <b>উদাহরণ:</b>
❌ <code>mardan 2</code> → ✅ <code>Mardaani 2</code>
❌ <code>psuhpa</code> → ✅ <code>Pushpa</code>
❌ <code>avnger</code> → ✅ <code>Avengers</code>

🔄 <b>আবার চেষ্টা করুন</b> সঠিক নাম লিখে।
"""
    
    await update.message.reply_text(
        text=message,
        parse_mode='HTML',
        reply_to_message_id=update.message.message_id
    )

async def send_multiple_movie_cards(update: Update, movies):
    """একাধিক মুভি কার্ড পাঠায় (প্রতিটি পোস্টার + বাটন সহ)"""
    if not movies:
        return
    
    for movie in movies[:3]:  # সর্বোচ্চ ৩টি
        await send_movie_result_with_image(update, movie)


async def send_trending_movies_cards(update: Update, context):
    """ট্রেন্ডিং ৩টি মুভি কার্ড পাঠায়"""
    if recommendation_engine:
        trending = recommendation_engine.get_trending_recommendations(3)
        if trending:
            await send_multiple_movie_cards(update, trending)
            return
    
    # ফ্যালব্যাক: কিছু জনপ্রিয় মুভি দেখাও
    fallback_movies = [
        {"title": "Diesel Full Movie", "year": "2025", "rating": "6.2"},
        {"title": "Pushpa 2", "year": "2024", "rating": "8.1"},
        {"title": "KGF Chapter 3", "year": "2025", "rating": "8.7"}
    ]
    await send_multiple_movie_cards(update, fallback_movies)

# bot.py - এই ফাংশনগুলো যোগ করুন (যেকোনো জায়গায়)

async def send_enhanced_movie_response(update, context, movie, user_id):
    """এনহ্যান্সড মুভি রেসপন্স (রিকমেন্ডেশন সহ)"""
    
    # বেসিক মুভি ইনফো
    message_text = format_movie_text(movie)
    
    # রিকমেন্ডেশন বাটন তৈরি
    keyboard = []
    
    # Similar Movies
    if recommendation_engine:
        similar = recommendation_engine.get_similar_movies(movie)
        if similar:
            row = []
            for m in similar[:3]:
                row.append(InlineKeyboardButton(
                    f"🎬 {m['title'][:15]}", 
                    callback_data=f"movie_{m['title']}"
                ))
            if row:
                keyboard.append(row)
    
    # Trending (যদি similar না থাকে)
    elif recommendation_engine:
        trending = recommendation_engine.get_trending_recommendations(3)
        if trending:
            row = []
            for m in trending:
                row.append(InlineKeyboardButton(
                    f"🔥 {m['title'][:15]}", 
                    callback_data=f"movie_{m['title']}"
                ))
            if row:
                keyboard.append(row)
    
    # ডাউনলোড বাটন
    if movie.get('detail_link'):
        keyboard.append([
            InlineKeyboardButton("📥 ডাউনলোড", url=movie['detail_link'])
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    # ইমেজ সহ পাঠান
    await send_movie_result_with_image(update, movie, message_text, reply_markup)


async def handle_not_found(update, context, query):
    """মুভি না পেলে সাজেশন দেখাবে"""
    
    suggestions = search_engine.find_similar_movies(query)
    
    if suggestions:
        keyboard = []
        for movie in suggestions[:3]:
            keyboard.append([InlineKeyboardButton(
                f"🎬 {movie['title']}", 
                callback_data=f"suggest_{movie['title']}"
            )])
        
        await update.message.reply_text(
            f"❌ '{query}' খুঁজে পাইনি। আপনি কি এইগুলোর কোনোটি খুঁজছেন?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            f"❌ '{query}' খুঁজে পাইনি।\n"
            f"রিকোয়েস্ট করতে: /req {query}"
        )

async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ইনলাইন বাটন ক্লিক হ্যান্ডল করবে - ক্লিন ভার্সন"""
    query = update.callback_query
    clicking_user = query.from_user
    clicking_user_id = clicking_user.id
    data = query.data
    
    print(f"🖱️ বাটন ক্লিক: {clicking_user.first_name} ({clicking_user_id}) -> {data}")
    
    # চ্যাটের টাইপ চেক করো
    chat_type = update.effective_chat.type
    
    # ✅ প্রথমে এডমিন বাটন চেক করো
    if data.startswith("req_done_"):
        request_id = int(data.replace("req_done_", ""))
        await handle_admin_done(update, context, request_id, clicking_user)
        return
    
    if data.startswith("req_later_"):
        request_id = int(data.replace("req_later_", ""))
        await handle_admin_later(update, context, request_id, clicking_user)
        return
    
    if data.startswith("req_reject_"):
        request_id = int(data.replace("req_reject_", ""))
        await handle_admin_reject(update, context, request_id, clicking_user)
        return
    
    # ✅ ইউজার-স্পেসিফিক বাটন থেকে ইউজার আইডি এক্সট্রাক্ট
    original_data, target_user_id = extract_user_from_callback(data)
    
    # শুধু গ্রুপ/সুপারগ্রুপে ইউজার-স্পেসিফিক চেক প্রয়োগ করো
    if chat_type in ['group', 'supergroup'] and target_user_id and target_user_id != clicking_user_id:
        await query.answer("⛔ এই বাটনটি আপনার জন্য নয়!", show_alert=True)
        return
    
    # এখন original_data দিয়ে কাজ করো
    data = original_data
    
    # ✅ এডমিন মেনু সিস্টেম
    admin_ids = config.ADMIN_USER_IDS
    
    if data in ["show_admin_commands", "close_menu"] or data.startswith("run_") or data.startswith("admin_"):
        if clicking_user_id not in admin_ids:
            await query.answer("⛔ শুধুমাত্র এডমিন", show_alert=True)
            return
    
    # এডমিন কমান্ডস মেনু
    if data == "show_admin_commands":
        await query.edit_message_text(
            text=admin_menu.get_commands_list(),
            reply_markup=admin_menu.create_commands_keyboard(),
            parse_mode='HTML'
        )
        return
    
    # কমান্ড রান
    elif data.startswith("run_"):
        cmd = f"/{data.replace('run_', '')}"
        await query.message.reply_text(cmd)
        await query.answer(f"✅ {cmd}", show_alert=False)
        return
    
    # মেনু ক্লোজ
    elif data == "close_menu":
        await query.delete_message()
        return
    
    # ✅ নতুন কনফার্মেশন বাটন
    elif data.startswith("confirm_yes_"):
        original_query = data.replace("confirm_yes_", "")
        await handle_confirmation_yes(update, context, original_query)
        await query.answer()
        return

    elif data.startswith("confirm_no_"):
        original_query = data.replace("confirm_no_", "")
        await handle_confirmation_no(update, context, original_query, clicking_user)
        await query.answer()
        return
    
    # ✅ সাজেশন থেকে মুভি সিলেক্ট
    elif data.startswith("select_movie_"):
        movie_title = data.replace("select_movie_", "")
        await handle_movie_selection(update, context, movie_title, clicking_user)
        await query.answer(f"✅ {movie_title} সিলেক্ট করা হয়েছে")
        return
    
    # ✅ হেল্প বাটন
    elif data == "show_search_guide":
        await show_search_guide(update, context)
        return
    
    elif data == "help_search":
        await show_help_search(update, context)
        return
    
    elif data == "link_coming_soon":
        await query.answer("⚠️ লিংক খুব দ্রুত অ্যাড করা হবে। অনুগ্রহ করে অপেক্ষা করুন...", show_alert=True)
        return
    
    else:
        print(f"⚠️ Unknown callback data: {data}")

    
# ========== HELPER FUNCTIONS ==========

async def show_help_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """হেল্প সার্চ গাইড দেখায়"""
    # callback_query থেকে মেসেজ পাঠানো
    if update.callback_query:
        query = update.callback_query
        await query.message.reply_text(
            "🆘 <b>সার্চ সাহায্য:</b>\n\n"
            "• <b>সঠিক নাম</b> ব্যবহার করুন\n"
            "• বাংলা বা ইংলিশ যেকোন ভাষায় লিখুন\n"
            "• স্পেলিং ভুল হলে বট অটো করেক্ট করবে\n"
            "• সমস্যা হলে এডমিনকে জানান",
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            "🆘 <b>সার্চ সাহায্য:</b>\n\n"
            "• <b>সঠিক নাম</b> ব্যবহার করুন\n"
            "• বাংলা বা ইংলিশ যেকোন ভাষায় লিখুন\n"
            "• স্পেলিং ভুল হলে বট অটো করেক্ট করবে\n"
            "• সমস্যা হলে এডমিনকে জানান",
            parse_mode='HTML'
        )


async def show_search_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """সার্চ গাইড দেখায়"""
    search_guide = """
🎬 <b>সঠিকভাবে মুভি সার্চ করার গাইড</b>

📝 <b>সার্চ ফরম্যাট:</b>
• শুধু মুভির নাম (বছর/কোয়ালিটি না)
• ইংলিশে লিখুন
• সংক্ষিপ্ত এবং সঠিক নাম

🔍 <b>জনপ্রিয় মুভি উদাহরণ:</b>
<code>Diesel</code> <code>RRR</code>

❌ <b>ভুল উপায়:</b>
<code>Diesel full movie hindi</code> → <code>Diesel</code>
<code>Avatar the way of water</code> → <code>Avatar</code>
<code>বাহুবলী</code> → <code>Bahubali</code>

🔄 <b>এখনই ট্রাই করুন সরাসরি মুভির নাম লেখুন</b>
<code>Diesel</code> অথবা <code>RRR</code>
"""
    # callback_query থেকে মেসেজ পাঠানো
    if update.callback_query:
        query = update.callback_query
        await query.message.reply_text(search_guide, parse_mode='HTML')
    else:
        await update.message.reply_text(search_guide, parse_mode='HTML')

# bot.py - handle_auto_search() ফাংশনে এই অংশটি খুঁজে বদল করুন

async def handle_auto_search(update: Update, query: str):
    """ইউজারের সরাসরি মুভি কোয়েরি হ্যান্ডল করবে"""
    try:
        print(f"🔍 অটো-সার্চ চালাচ্ছি: '{query}'")
        
        # ১. এক্সাক্ট সার্চ
        results = search_engine.search_movies(query)
        
        if not results:
            # কোনো রেজাল্ট না পাওয়া
            await handle_no_results(update, query)
            return
        
        best_match = results[0]
        match_score = search_engine.calculate_match_score(best_match, query)
        
        print(f"🎯 বেস্ট ম্যাচ: '{best_match['title']}' (স্কোর: {match_score})")
        
        # ২. ম্যাচ কোয়ালিটি based action
        if match_score >= 90:  # এক্সাক্ট ম্যাচ (90%+)
            # ✅ যদি ১টির বেশি মুভি থাকে
            if len(results) > 1:
                await update.message.reply_text(
                    f"🎬 <b>'{query}' - পাওয়া ভার্সনগুলো ({len(results)} টি):</b>",
                    parse_mode='HTML'
                )
                
                # প্রথম ৩টি মুভি পাঠাবে
                for movie in results[:3]:
                    await send_movie_result_with_image(update, movie)
                
                # যদি আরও বেশি থাকে
                if len(results) > 3:
                    await update.message.reply_text(
                        f"📦 <i>এবং আরও {len(results) - 3} টি মুভি...</i>",
                        parse_mode='HTML'
                    )
            else:
                # শুধু ১টি থাকলে
                await send_direct_result(update, best_match)
        
        elif match_score >= 70:  # পার্শিয়াল ম্যাচ - কনফার্মেশন
            await ask_confirmation(update, query, best_match)
        
        else:  # লো কনফিডেন্স - সাজেশন
            await show_search_suggestions(update, query, results[:3])
            
    except Exception as e:
        print(f"❌ অটো-সার্চ এরর: {e}")
        # ✅ সঠিকভাবে ফরম্যাট করা error মেসেজ
        error_message = f"""
⚠️ <b>'{query}' নামে সার্চ করতে সমস্যা হচ্ছে</b>

🔍 <b>সমাধানের উপায়:</b>
• মুভির সঠিক নাম ব্যবহার করুন
• ছোট করে লিখুন (শুধু মূল নাম)
• ইংলিশে লিখুন
• স্পেসিং চেক করুন

📝 <b>উদাহরণ:</b>
<code>Diesel</code> 
<code>Devara</code> 

<b>এভাবে চেষ্টা করার পর যদি মুভি না পান তাহলে মুভি রিকোয়েস্ট করুন নিচের দেয়া নিয়মে</b>

<code>/req RRR 2023</code>
<code>/req Diesel 2025</code>

🔄 <b>আবার চেষ্টা করুন</b>
"""
        await update.message.reply_text(
            error_message, 
            parse_mode='HTML',
            reply_to_message_id=update.message.message_id,
            disable_web_page_preview=True
        )

async def send_direct_result(update: Update, movie: dict):
    """সরাসরি মুভি রেজাল্ট পাঠাবে"""
    try:
        # সিরিজ চেক করবে
        series_movies = search_engine.get_movie_series(movie['title'])
        
        if len(series_movies) > 1:
            # মাল্টিপার্ট মুভি - সব পার্ট পাঠাবে
            await update.message.reply_text(f"🎬 {movie['title']} - সিরিজের সব পার্ট:")
            for series_movie in series_movies:
                await send_movie_result_with_image(update, series_movie)
        else:
            # সিঙ্গেল মুভি
            await send_movie_result_with_image(update, movie)
            
    except Exception as e:
        print(f"❌ ডিরেক্ট রেজাল্ট send এরর: {e}")
        await update.message.reply_text(
            f"🎬 {movie['title']}\n\n" +
            "ডাউনলোড লিংক পেতে নিচের বাটনে ক্লিক করুন 👇",
            reply_markup=create_movie_results_keyboard([movie])
        )

async def ask_confirmation(update: Update, original_query: str, suggested_movie: dict):
    """স্পেলিং করেকশনের জন্য কনফার্মেশন ask করবে"""
    keyboard = [
        [
            InlineKeyboardButton(
                f"✅ হ্যাঁ, {suggested_movie['title']}",
                callback_data=f"confirm_{suggested_movie['title']}"
            ),
            InlineKeyboardButton(
                "❌ না, অন্য মুভি", 
                callback_data=f"deny_{original_query}"
            )
        ]
    ]
    
    await update.message.reply_text(
        f"🤔 আপনি কি '{suggested_movie['title']}' খুঁজছেন?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        reply_to_message_id=update.message.message_id
    )

async def show_search_suggestions(update: Update, query: str, suggestions: list):
    """সার্চ সাজেশন দেখাবে"""
    if not suggestions:
        await handle_no_results(update, query)
        return
    
    suggestion_text = f"🔍 '{query}' এর জন্য সাজেশন:\n\n"
    
    for i, movie in enumerate(suggestions[:3], 1):
        year_text = f" ({movie.get('year', '')})" if movie.get('year') else ""
        suggestion_text += f"{i}. {movie['title']}{year_text}\n"
    
    suggestion_text += "\nসঠিক মুভি সিলেক্ট করতে নিচের বাটনে ক্লিক করুন 👇"
    
    keyboard = []
    for movie in suggestions[:3]:
        keyboard.append([
            InlineKeyboardButton(
                f"🎬 {movie['title']}", 
                callback_data=f"suggest_{movie['title']}"
            )
        ])
    
    await update.message.reply_text(
        suggestion_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        reply_to_message_id=update.message.message_id
    )

# bot.py - handle_no_results() ফাংশনেও আপডেট করুন

async def handle_no_results(update: Update, query: str):
    """কোনো রেজাল্ট না পাওয়ার হ্যান্ডলিং"""
    similar_movies = search_engine.find_similar_movies(query)
    
    if similar_movies:
        await show_similar_suggestions(update, query, similar_movies)
    else:
        # ✅ উন্নত error মেসেজ
        error_guide = f"""
❌ **'{query}' নামে কোনো মুভি পাওয়া যায়নি**

🔍 **সার্চ উন্নত করার টিপস:**

• **বানান চেক করুন** - `avnger` ❌ → `avengers` ✅
• **সংক্ষিপ্ত লিখুন** - `avatar the way of water` ❌ → `avatar` ✅  
• **ইংলিশ ব্যবহার করুন** - `বাহুবলী` ❌ → `bahubali` ✅
• **বছর বাদ দিন** - `kgf 2022` ❌ → `kgf` ✅

📋 **জনপ্রিয় মুভি উদাহরণ:**
`kgf`, `rrr`, `avatar`, `avengers`, `dhoom`, `bahubali`

🎯 **আবার চেষ্টা করুন - সংক্ষিপ্ত এবং সঠিক নাম লিখুন:**
`{query.split()[0] if query.split() else query}`
"""
        await update.message.reply_text(
            error_guide,
            parse_mode='Markdown',
            reply_to_message_id=update.message.message_id
        )

async def show_similar_suggestions(update: Update, query: str, similar_movies: list):
    """সিমিলার মুভি সাজেশন দেখাবে"""
    suggestion_text = f"❌ '{query}' নামে কোনো মুভি নেই।\n\n" + \
                     "🤔 আপনি কি নিচের কোনো মুভি খুঁজছেন?\n\n"
    
    for i, movie in enumerate(similar_movies[:3], 1):
        suggestion_text += f"{i}. {movie['title']}\n"
    
    keyboard = []
    for movie in similar_movies[:3]:
        keyboard.append([
            InlineKeyboardButton(
                f"🎯 {movie['title']}", 
                callback_data=f"suggest_{movie['title']}"
            )
        ])
    
    await update.message.reply_text(
        suggestion_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        reply_to_message_id=update.message.message_id
    )

# স্টার্ট কমান্ড হ্যান্ডলার
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    admin_ids = [6723820690]
    
    if user.id in admin_ids:
        # ✅ এডমিন হলে ফিক্সড কীবোর্ড সেট করব
        welcome_text = f"""
👋 <b>এডমিন প্যানেলে স্বাগতম!</b>

📊 মুভি: {cache_manager.get_movie_count()} টি
🔄 শেষ আপডেট: {cache_manager.cache_data.get('last_updated', 'N/A')}

👇 <b>নিচের বাটন ব্যবহার করুন</b>
"""
        await update.message.reply_text(
            text=welcome_text,
            reply_markup=admin_menu.create_fixed_admin_keyboard(),  # ✅ ফিক্সড কীবোর্ড
            parse_mode='HTML'
        )
    else:
        # সাধারণ ইউজার
        await update.message.reply_text(
            text=WELCOME_MESSAGE.format(user_mention=user.first_name),
            reply_markup=create_welcome_keyboard(),
            parse_mode='HTML'
        )
    
    print(f"👋 ইউজার: {user.first_name} - এডমিন: {user.id in admin_ids}")


async def handle_admin_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ফিক্সড কীবোর্ডের বাটন ক্লিক হ্যান্ডল করবে"""
    user = update.message.from_user
    text = update.message.text
    
    # শুধু এডমিন
    if user.id != 6723820690:
        return
    
    if text == "🤖 এডমিন কমান্ড লিস্ট":
        await update.message.reply_text(
            text=admin_menu.get_commands_list_text(),
            reply_markup=admin_menu.create_inline_commands_keyboard(),
            parse_mode='HTML'
        )
    
    elif text == "📊 ক্যাশ স্ট্যাটাস":
        await update.message.reply_text("/cache_status")
    
    elif text == "🔄 রিফ্রেশ":
        await update.message.reply_text("/refresh")



# গ্রুপে নতুন মেম্বার জয়েন করলে ওয়েলকাম মেসেজ
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """যখন নতুন ইউজার গ্রুপে জয়েন করবে - চ্যানেলে না"""
    try:
        # চ্যানেলে হলে কিছু করবে না
        if update.message.chat.type == 'channel':
            return
        
        # শুধু গ্রুপ এবং সুপারগ্রুপে কাজ করবে
        if update.message.chat.type not in ['group', 'supergroup']:
            return
        
        for member in update.message.new_chat_members:
            if member.id == context.bot.id:
                # বট নিজে জয়েন করলে
                await update.message.reply_text(
                    "ধন্যবাদ! আমাকে গ্রুপে এড করার জন্য। 🎬\n"
                    "আমি মুভি সার্চ এবং প্রশ্নের উত্তর দিতে সাহায্য করব।"
                )
            else:
                # সাধারণ ইউজার জয়েন করলে
                user_mention = f"@{member.username}" if member.username else member.first_name
                
                # ১. প্রথমে ওয়েলকাম মেসেজ পাঠাবে
                await update.message.reply_text(
                    text=WELCOME_MESSAGE.format(user_mention=user_mention),
                    reply_markup=create_welcome_keyboard(),
                    parse_mode='HTML'
                )
                
                # ২. সার্চ গাইড
                await asyncio.sleep(2)
                search_guide = f"""
🔍 {user_mention} - <b>মুভি সার্চ সিস্টেম গাইড 🎬</b>

<b>📋 সার্চ করার ২টি সহজ উপায়:</b>

1️⃣ <b>সরাসরি মুভির নাম লিখুন</b>
✨ শুধু মুভির নাম গ্রুপে লিখলেই হবে
📝 উদাহরণ: <code>diesel</code> বা <code>devara</code>

2️⃣ <b>সার্চ কমান্ড ব্যবহার করুন</b>  
🔧 <code>/search মুভির_নাম</code>
📝 উদাহরণ: <code>/search diesel</code> বা <code>/search devara</code>
"""
                
                await update.message.reply_text(
                    text=search_guide,
                    parse_mode='HTML',
                    disable_web_page_preview=True
                )
                
                print(f"👥 গ্রুপে নতুন ইউজার: {member.first_name}")
                
    except Exception as e:
        print(f"❌ ওয়েলকাম মেসেজ এরর: {e}")

def create_movie_results_keyboard(movies):
    """মুভি রেজাল্টের জন্য বাটন তৈরি করবে - লিংক unavailable সহ"""
    keyboard = []
    for movie in movies:
        movie_link = movie.get('detail_link')
        
        button_text = f"🎬 {movie['title']}"
        if movie.get('year'):
            button_text += f" ({movie['year']})"
        
        # ✅ যদি লিংক থাকে তাহলে URL বাটন, না থাকলে callback বাটন
        if movie_link:
            keyboard.append([
                InlineKeyboardButton(button_text, url=movie_link)
            ])
        else:
            keyboard.append([
                InlineKeyboardButton(f"⏳ {button_text} - লিংক আসছে...", callback_data="link_coming_soon")
            ])
    
    return InlineKeyboardMarkup(keyboard)

# হেল্প কমান্ড হ্যান্ডলার
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """যখন ইউজার /help কমান্ড দিবে"""
    help_text = """
📋 কমান্ড লিস্ট:

/start - বট শুরু করুন
/help - সাহায্য দেখুন
/search [মুভি নাম] - মুভি সার্চ করুন

🎬 মুভি সার্চ উদাহরণ:
<code>/search ইনসেপশন</code>
<code>/search avengers endgame</code> 
<code>/search বাংলা মুভি</code>

💬 গ্রিটিংস: হাই, হ্যালো, Hello, Hi লিখলেও রেসপন্স পাবেন
    """
    await update.message.reply_text(help_text)



async def refresh_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """অটো রিফ্রেশ স্ট্যাটাস চেক করবে"""
    if auto_refresher:
        status = "চালু 🟢" if auto_refresher.is_running else "বন্ধ 🔴"
        next_check = "সক্রিয়" if auto_refresher.is_running else "নিষ্ক্রিয়"
        
        message = f"""
🔄 **অটো রিফ্রেশ স্ট্যাটাস:**

• **স্ট্যাটাস:** {status}
• **পরবর্তী চেক:** {next_check}
• **ইন্টারভাল:** ৩০ মিনিট
• **ক্যাশে মুভি:** {cache_manager.get_movie_count()} টি

ℹ️ প্রতি ৩০ মিনিট পর স্বয়ংক্রিয়ভাবে নতুন মুভি চেক করা হবে
"""
    else:
        message = "❌ অটো রিফ্রেশার ইনিশিয়ালাইজ হয়নি"
    
    await update.message.reply_text(message, parse_mode='Markdown')


# এরর হ্যান্ডলার
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """এরর হ্যান্ডল করবে"""
    logger.error(f"এরর: {context.error}")

# গ্লোবাল ভেরিয়েবল
cache_manager = None
search_engine = None
scraper = None
blogger_api = None  
auto_refresher = None
message_classifier = None
channel_poster = None  
request_manager = None  
admin_notifier = None   
admin_menu = None

# NEW GLOBAL VARIABLES
ai_agent = None
user_profile_manager = None
learning_system = None
context_memory = None
recommendation_engine = None
local_ai_agent = None   # ✅ এই লাইনটা ঠিক আছে (global ছাড়া)


# bot.py - initialize_services() ফাংশন আপডেট করুন

def initialize_services():
    """সার্ভিসেস ইনিশিয়ালাইজ করবে - আপডেটেড ভার্সন"""
    global cache_manager, search_engine, blogger_api, auto_refresher
    global message_classifier, channel_poster, request_manager, admin_notifier
    global admin_menu, user_profile_manager, learning_system
    global context_memory, recommendation_engine
    global local_ai_agent
    
    print("="*50)
    print("🔄 সার্ভিস ইনিশিয়ালাইজেশন শুরু...")
    
    # ========== বেসিক সার্ভিস ==========
    cache_manager = CacheManager()
    search_engine = SearchEngine(cache_manager)
    print("✅ Cache & Search Engine Ready")
    
    # ব্লগার API setup
    blogger_api = BloggerAPI(config.BLOGGER_BLOGS)
    print("✅ Blogger API Ready")
    
    # চ্যানেল পোস্টার
    from channel_poster import ChannelPoster
    channel_poster = ChannelPoster(cache_manager)
    print("✅ Channel Poster Ready")
    
    # রিকোয়েস্ট ম্যানেজার
    request_manager = RequestManager(config.REQUEST_FILE)
    print("✅ Request Manager Ready")
    
    # এডমিন নোটিফায়ার
    admin_notifier = AdminNotifier(
        admin_user_ids=config.ADMIN_USER_IDS,
        notification_channel_id=config.REQUEST_NOTIFICATION_CHANNEL
    )
    print("✅ Admin Notifier Ready")
    
    # ========== প্রোফাইল ও লার্নিং সিস্টেম ==========
    user_profile_manager = UserProfileManager(config.USER_PROFILES_FILE)
    learning_system = LearningSystem(config.LEARNING_CACHE_FILE)
    context_memory = ContextMemory()
    print("✅ Profile & Learning Systems Ready")
    
    # ========== লোকাল এআই এজেন্ট ==========
    from local_ai_agent import LocalAIAgent
    local_ai_agent = LocalAIAgent(cache_manager, user_profile_manager, learning_system)
    print("✅ Local AI Agent Ready")
    
    # ========== মেসেজ ক্লাসিফায়ার (ইম্প্রুভড) ==========
    # নতুন আপডেটেড ক্লাসিফায়ার ব্যবহার
    from message_classifier import MessageClassifier
    message_classifier = MessageClassifier(cache_manager, local_ai_agent)
    print("✅ Improved Message Classifier Ready")
    
    # ========== রিকমেন্ডেশন ইঞ্জিন ==========
    recommendation_engine = RecommendationEngine(
        cache_manager, 
        user_profile_manager, 
        learning_system
    )
    print("✅ Recommendation Engine Ready")
    
    # ========== অটো রিফ্রেশার ==========
    from auto_refresher import AutoRefresher
    auto_refresher = AutoRefresher(
        blogger_api, 
        cache_manager, 
        search_engine, 
        request_manager
    )
    print("✅ Auto Refresher Ready")
    
    # ========== এডমিন মেনু ==========
    admin_menu = ShortAdminMenu()
    print("✅ Admin Menu Ready")
    
    # ========== ব্লগার থেকে ডাটা লোড ==========
    if cache_manager.needs_update() or cache_manager.get_movie_count() == 0:
        print("🔄 Loading real movie data from Blogger...")
        real_movies = blogger_api.get_all_posts_from_all_blogs()
        
        if real_movies:
            cache_manager.update_movies(real_movies)
            print(f"✅ {len(real_movies)} movies loaded")
        else:
            print("⚠️ No movies loaded from Blogger")
    
    print(f"✅ All Services Ready! Total Movies: {cache_manager.get_movie_count()}")
    print("="*50)

# bot.py-তে এই ফাংশন যোগ করুন
async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """সার্চ কমান্ড হ্যান্ডলার - ইম্প্রুভড ভার্সন"""
    if not context.args:
        user = update.message.from_user
        user_mention = f"@{user.username}" if user.username else user.first_name
        
        await update.message.reply_text(
            text=f"""
🔍 {user_mention} - <b>মুভি সার্চ সিস্টেম গাইড 🎬</b>

<b>📋 সার্চ করার ২টি সহজ উপায়:</b>

1️⃣ <b>সরাসরি মুভির নাম লিখুন</b>
   ✨ শুধু মুভির নাম গ্রুপে লিখলেই হবে
   📝 উদাহরণ: <code>diesel</code> বা <code>devara</code>

2️⃣ <b>সার্চ কমান্ড ব্যবহার করুন</b>  
   🔧 <code>/search মুভির_নাম</code>
   📝 উদাহরণ: <code>/search diesel</code> 
               <code>/search devara</code>

<b>🎯 সঠিক সার্চ উদাহরণ:</b>
✅ <code>diesel</code> 
✅ <code>avatar</code> 
✅ <code>devara</code> 

<b>💡 স্মার্ট ফিচার:</b>
• ইংলিশে লিখুন - সবচেয়ে ভালো রেজাল্ট
• স্পেলিং ভুলে অটো করেকশন
• একই সিরিজের সব পার্ট দেখাবে
• পোস্টার ইমেজ সহ রেজাল্ট

<b>🚀 এখনই ট্রাই করুন - যেকোনো একটি লিখুন:</b>
<code>diesel</code> অথবা <code>devara</code> অথবা <code>/search NeelChokro</code>

👇 <b>সার্চ শুরু করতে এখনই লিখুন...</b>
""",
            parse_mode='HTML',
            disable_web_page_preview=True
        )
        return
    
    query = ' '.join(context.args)
    user = update.message.from_user
    
    print(f"🔍 সার্চ রিকুয়েস্ট: {user.first_name} -> '{query}'")
    
    # MarkdownV2 এর জন্য বিশেষ ক্যারেক্টার escape করার ফাংশন - ফিক্সড
    def escape_markdown(text):
        escape_chars = r'_*[]()~`>#+-=|{}.!'
        return ''.join(['\\' + char if char in escape_chars else char for char in text])
    
    # ১. প্রথমে এক্সাক্ট ম্যাচ খুঁজবে
    results = search_engine.search_movies(query)
    
    if results:
        # এক্সাক্ট ম্যাচ আছে কিনা চেক
        exact_match = False
        for movie in results:
            if query.lower() == movie['title'].lower():
                exact_match = True
                break
        
        if exact_match:
            # ২. এক্সাক্ট ম্যাচ থাকলে সব পার্টসহ পাঠাবে
            series_movies = search_engine.get_movie_series(results[0]['title'])
            
            if len(series_movies) > 1:
                # মাল্টিপার্ট মুভি - সব পার্ট পাঠাবে
                for movie in series_movies:
                    await send_movie_result_with_image(update, movie)
            else:
                # সিঙ্গেল মুভি - শুধু সেই মুভিটি পাঠাবে
                await send_movie_result_with_image(update, results[0])
        else:
            # ৩. এক্সাক্ট ম্যাচ না থাকলে (স্পেলিং ভুল)
            suggested_movie = results[0]  # বেস্ট ম্যাচ
            user_mention = f"@{user.username}" if user.username else user.first_name
            
            # কপি করার জন্য রেডিমেড কমান্ড তৈরি
            correct_search_command = f"/search {suggested_movie['title']}"
            escaped_title = escape_markdown(suggested_movie['title'])
            escaped_command = escape_markdown(correct_search_command)
            escaped_mention = escape_markdown(user_mention)
            
            notification_message = f"""
🔍 {escaped_mention}, আপনি কি *"{escaped_title}"* মুভিটি খুঁজছেন?

📝 *সঠিক সার্চ কমান্ড:*
`{escaped_command}`

1️⃣ উপরের কমান্ড টেক্সটটিতে ক্লিক করুন কপি হয়ে যাবে
2️⃣ গ্রুপে পেস্ট করুন  
3️⃣ সেন্ড বাটনে ক্লিক করুন

🎬 তাহলে আপনি *"{escaped_title}"* মুভিটি পেয়ে যাবেন\\!
"""
            
            await update.message.reply_text(
                notification_message,
                parse_mode='MarkdownV2',
                reply_to_message_id=update.message.message_id
            )
    else:
        # ৪. কোনো ম্যাচই না থাকলে
        await update.message.reply_text(
            f"😔 '{query}' নামে কোনো মুভি পাওয়া যায়নি।\\n\\n"
            "দয়া করে সঠিক নাম ব্যবহার করুন অথবা এডমিনকে জানান\\.",
            parse_mode='MarkdownV2',
            reply_to_message_id=update.message.message_id
        )

def format_movie_result(movie):
    """মুভি রেজাল্ট ফরম্যাট করবে - লিংক unavailable সহ"""
    # ✅ লিংক available কিনা চেক করবে
    movie_link = movie.get('detail_link')
    
    quality_text = f"• <b>কোয়ালিটি:</b> {movie.get('quality', 'HD')}\n" if movie.get('quality') else ""
    year_text = f"• <b>সাল:</b> {movie.get('year', 'N/A')}\n" if movie.get('year') else ""
    genre_text = f"• <b>জেনার:</b> {movie.get('genre', 'N/A')}\n" if movie.get('genre') else ""
    rating_text = f"• <b>রেটিং:</b> {movie.get('rating', 'N/A')}\n" if movie.get('rating') else ""
    
    # ✅ যদি লিংক না থাকে
    if not movie_link:
        return f"""
🎬 <b>{movie['title']}</b>

{year_text}{quality_text}{genre_text}{rating_text}⚠️ <b>লিংক খুব দ্রুত অ্যাড করা হবে</b>
<b>অনুগ্রহ করে অপেক্ষা করুন...</b>
"""
    
    # ✅ যদি লিংক থাকে
    return f"""
🎬 <b>{movie['title']}</b>

{year_text}{quality_text}{genre_text}{rating_text}• <b>ডাউনলোড:</b> নিচের বাটনে ক্লিক করুন 👇
    """


async def is_user_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ইউজার এডমিন কিনা চেক করবে - অ্যানোনিমাস অ্যাডমিন সাপোর্ট সহ"""
    try:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        chat_type = update.effective_chat.type
        
        # ১. অ্যানোনিমাস অ্যাডমিন চেক (টেলিগ্রাম স্পেশাল আইডি)
        if user_id == 1087968824:  # অ্যানোনিমাস অ্যাডমিন
            print(f"👑 অ্যানোনিমাস এডমিন ডিটেক্ট: {user_id}")
            return True
        
        # ২. পার্সোনাল চ্যাটে সবাইকে এডমিন হিসেবে গণ্য করব
        if chat_type == 'private':
            return True
        
        # ৩. config-এর এডমিন লিস্টে আছে কিনা চেক
        if user_id in config.ADMIN_USER_IDS:
            print(f"👑 এডমিন (হোয়াইটলিস্ট): {user_id}")
            return True
        
        # ৪. গ্রুপ/সুপারগ্রুপে এডমিন চেক
        if chat_type in ['group', 'supergroup']:
            try:
                chat_member = await context.bot.get_chat_member(chat_id, user_id)
                is_admin = chat_member.status in ['creator', 'administrator']
                
                if is_admin:
                    print(f"👑 গ্রুপ এডমিন ডিটেক্ট: {user_id}")
                else:
                    print(f"👤 সাধারণ ইউজার: {user_id}")
                
                return is_admin
                
            except Exception as e:
                print(f"⚠️ get_chat_member এরর: {e}")
                return user_id in config.ADMIN_USER_IDS
        
        return False
        
    except Exception as e:
        print(f"❌ এডমিন চেক ব্যর্থ: {e}")
        return False

async def mute_user_permanently(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ইউজারকে পারমানেন্টলি মিউট করবে - অ্যানোনিমাস এডমিন সুরক্ষা সহ"""
    try:
        user = update.message.from_user
        user_id = user.id
        chat_id = update.message.chat_id
        
        # 🔒 অ্যানোনিমাস এডমিন চেক
        if user_id == 1087968824:
            print(f"⚠️ অ্যানোনিমাস এডমিনকে মিউট করার চেষ্টা ব্লক করা হয়েছে")
            # মেসেজ ডিলিট করব না, শুধু লগ রাখব
            return
        
        # 🔒 এডমিন চেক (হোয়াইটলিস্ট)
        if user_id in config.ADMIN_USER_IDS:
            print(f"⚠️ এডমিনকে মিউট করার চেষ্টা ব্লক: {user_id}")
            return
        
        # গ্রুপ এডমিন চেক
        try:
            chat_member = await context.bot.get_chat_member(chat_id, user_id)
            if chat_member.status in ['creator', 'administrator']:
                print(f"⚠️ গ্রুপ এডমিনকে মিউট করার চেষ্টা ব্লক: {user_id}")
                return
        except:
            pass
        
        print(f"🔇 সাধারণ ইউজার মিউট করা হচ্ছে: {user.first_name} (ID: {user_id})")
        
        # ১. মেসেজ ডিলিট
        await update.message.delete()
        print("✅ মেসেজ ডিলিট করা হয়েছে")
        
        # ২. মিউট
        permissions = ChatPermissions(can_send_messages=False)
        
        await context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=permissions,
            until_date=None
        )
        print(f"✅ ইউজার মিউট করা হয়েছে: {user_id}")
        
        # ৩. নোটিফিকেশন
        mute_notification = f"""
🚫 <b>স্প্যামার ডিটেক্টেড!</b>

❌ ইউজার: {user.first_name} (ID: {user_id})
📛 কারণ: লিংক শেয়ার করা
⏰ সময়: {datetime.now().strftime("%Y-%m-%d %I:%M %p")}

⚠️ <b>গ্রুপ রুলস ভঙ্গ করায় ইউজারকে মিউট করা হয়েছে</b>
"""
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=mute_notification,
            parse_mode='HTML'
        )
        
    except Exception as e:
        print(f"❌ মিউট করতে সমস্যা: {e}")
        import traceback
        print(f"🔍 এরর ডিটেইলস: {traceback.format_exc()}")

# ================== AUTO RESPONSE FUNCTIONS (NEW) ==================

# ইউজারের শেষ রেসপন্স ট্র্যাক করার জন্য
user_last_response = {}

def check_auto_response_keywords(message_text):
    """মেসেজে অটো রেসপন্স কীওয়ার্ড আছে কিনা চেক করে"""
    if not message_text:
        return False
    
    message_lower = message_text.lower()
    
    for category, keywords in config.AUTO_RESPONSE_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in message_lower:
                print(f"🔑 কীওয়ার্ড ডিটেক্ট: '{keyword}' (category: {category})")
                return True
    
    return False

def is_cooldown_active(user_id):
    """ইউজারের জন্য কুলডাউন চেক করে"""
    global user_last_response
    
    if user_id in user_last_response:
        last_time = user_last_response[user_id]
        cooldown = config.AUTO_RESPONSE_SETTINGS.get('cooldown_seconds', 30)
        if (datetime.now() - last_time).total_seconds() < cooldown:
            return True
    return False

def update_cooldown(user_id):
    """ইউজারের শেষ রেসপন্স সময় আপডেট করে"""
    global user_last_response
    user_last_response[user_id] = datetime.now()

def contains_any_link(text):
    """যেকোনো লিংক চেক করবে"""
    if not text:
        return False
        
    link_patterns = [
        r'http[s]?://', r'www\.', r't\.me/', 
        r'telegram\.me/', r'[\w]+\.[a-z]{2,}',
        r'bit\.ly/', r'goo\.gl/', r'tinyurl\.com',
        r'click\.here', r'download\.now'
    ]
    
    text_lower = text.lower()
    
    for pattern in link_patterns:
        if re.search(pattern, text_lower):
            return True
    return False

# ================== নতুন ইমেজ ফাংশন ================== 
async def send_movie_result_with_image(update: Update, movie, message_text=None):
    """ইমেজ সহ মুভি রেজাল্ট send করবে"""
    try:
        chat_id = update.effective_chat.id
        
        # ডিফল্ট মেসেজ টেক্সট
        if not message_text:
            message_text = format_movie_text(movie)
        
        # ✅ যদি ইমেজ URL থাকে
        if movie.get('image_url'):
            try:
                await update.message.reply_photo(
                    photo=movie['image_url'],
                    caption=message_text,
                    parse_mode='HTML',
                    reply_markup=create_movie_results_keyboard([movie])
                )
                print(f"🖼️ ইমেজ সহ রেজাল্ট send করা হয়েছে: {movie['title']}")
                return True
                
            except Exception as e:
                print(f"❌ ইমেজ send করতে সমস্যা: {e}")
                # fallback: শুধু টেক্সট send করবে
                print("🔄 ইমেজ send失败, টেক্সট fallback ব্যবহার করছি...")
        
        # ✅ fallback: শুধু টেক্সট send করবে
        await update.message.reply_text(
            message_text,
            parse_mode='HTML',
            reply_markup=create_movie_results_keyboard([movie]),
            disable_web_page_preview=False
        )
        print(f"📄 টেক্সট রেজাল্ট send করা হয়েছে: {movie['title']}")
        return True
        
    except Exception as e:
        print(f"❌ রেজাল্ট send করতে সমস্যা: {e}")
        return False


async def test_image_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ইমেজ সিস্টেম টেস্ট করার কমান্ড"""
    try:
        movies = cache_manager.get_all_movies()
        
        if not movies:
            await update.message.reply_text("❌ কোনো মুভি নেই")
            return
        
        # ইমেজ URL সহ মুভি খুঁজবে
        movies_with_images = [m for m in movies if m.get('image_url')]
        
        if movies_with_images:
            test_movie = movies_with_images[0]
            await update.message.reply_text(f"🔍 ইমেজ সিস্টেম টেস্ট করছি...")
            success = await send_movie_result_with_image(update, test_movie)
            
            if success:
                await update.message.reply_text("✅ ইমেজ সিস্টেম কাজ করছে!")
            else:
                await update.message.reply_text("❌ ইমেজ সিস্টেমে সমস্যা আছে")
        else:
            await update.message.reply_text("❌ কোনো মুভিতে ইমেজ URL নেই")
            
    except Exception as e:
        await update.message.reply_text(f"❌ টেস্ট করতে সমস্যা: {e}")
        print(f"❌ test_image_system এরর: {e}")

        
def format_movie_text(movie):
    """মুভির টেক্সট ফরম্যাট করবে (ইমেজ ক্যাপশনের জন্য)"""
    quality_text = f"• <b>কোয়ালিটি:</b> {movie.get('quality', 'HD')}\n" if movie.get('quality') else ""
    year_text = f"• <b>সাল:</b> {movie.get('year', 'N/A')}\n" if movie.get('year') else ""
    rating_text = f"• <b>রেটিং:</b> {movie.get('rating', 'N/A')}\n" if movie.get('rating') else ""
    genre_text = f"• <b>জেনার:</b> {movie.get('genre', 'N/A')}\n" if movie.get('genre') else ""
    
    movie_link = movie.get('detail_link')
    
    if not movie_link:
        return f"""
🎬 <b>{movie['title']}</b>

{year_text}{quality_text}{rating_text}{genre_text}⚠️ <b>লিংক খুব দ্রুত অ্যাড করা হবে</b>
<b>অনুগ্রহ করে অপেক্ষা করুন...</b>
"""
    
    return f"""
🎬 <b>{movie['title']}</b>

{year_text}{quality_text}{rating_text}{genre_text}• <b>ডাউনলোড:</b> নিচের বাটনে ক্লিক করুন 👇
"""

async def handle_chat_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """চ্যাট মেম্বার আপডেট ডিটেক্ট করবে - শুধু গ্রুপে"""
    try:
        if update.chat_member:
            # চ্যানেলে হলে কিছু করবে না
            if update.chat_member.chat.type == 'channel':
                return
            
            # শুধু গ্রুপ এবং সুপারগ্রুপে কাজ করবে
            if update.chat_member.chat.type not in ['group', 'supergroup']:
                return
            
            new_member = update.chat_member.new_chat_member
            old_member = update.chat_member.old_chat_member
            
            # ইউজার জয়েন/লিভ ডিটেক্ট
            if (new_member.status == 'member' and 
                old_member.status in ['left', 'kicked', 'restricted']):
                
                user = new_member.user
                user_mention = f"@{user.username}" if user.username else user.first_name
                chat_id = update.chat_member.chat.id
                
                print(f"✅ চ্যাট মেম্বার আপডেট (গ্রুপ): {user.first_name} জয়েন করেছেন")
                
                # ১. প্রথমে ওয়েলকাম মেসেজ পাঠাবে
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=WELCOME_MESSAGE.format(user_mention=user_mention),
                    reply_markup=create_welcome_keyboard(),
                    parse_mode='HTML'
                )
                
                # ২. সার্চ গাইড
                await asyncio.sleep(2)
                
                search_guide = f"""
🔍 {user_mention} - <b>মুভি সার্চ সিস্টেম গাইড 🎬</b>

<b>📋 সার্চ করার ২টি সহজ উপায়:</b>

1️⃣ <b>সরাসরি মুভির নাম লিখুন</b>
✨ শুধু মুভির নাম গ্রুপে লিখলেই হবে
📝 উদাহরণ: <code>diesel</code> বা <code>devara</code>

2️⃣ <b>সার্চ কমান্ড ব্যবহার করুন</b>  
🔧 <code>/search মুভির_নাম</code>
📝 উদাহরণ: <code>/search diesel</code> বা <code>/search devara</code>
"""
                
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=search_guide,
                    parse_mode='HTML',
                    disable_web_page_preview=True
                )
                
    except Exception as e:
        print(f"❌ চ্যাট মেম্বার আপডেট এরর: {e}")


async def refresh_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ম্যানুয়াল রিফ্রেশ কমান্ড - FIXED VERSION"""
    try:
        user = update.message.from_user
        
        # এডমিন চেক (আপনার আইডি)
        is_admin = user.id in [6723820690]
        
        if not is_admin:
            await update.message.reply_text("⛔ শুধুমাত্র এডমিন")
            return
        
        # ইউজারকে জানানো
        await update.message.reply_text("🔄 ব্লগার চেক করা হচ্ছে...")
        
        # ১. ব্লগার থেকে সব মুভি আনব
        print(f"🔍 {user.first_name} রিফ্রেশ কমান্ড দিয়েছেন")
        new_movies_data = blogger_api.get_all_posts_from_all_blogs()
        
        if not new_movies_data:
            await update.message.reply_text(
                "❌ ব্লগার থেকে কোনো মুভি লোড হয়নি\n"
                "⚠️ ইন্টারনেট কানেকশন বা API সমস্যা"
            )
            return
        
        print(f"📥 ব্লগারে মোট মুভি: {len(new_movies_data)} টি")
        
        # ২. বর্তমান ক্যাশে মুভি
        current_movies = cache_manager.get_all_movies()
        current_count = len(current_movies)
        print(f"📊 বর্তমান ক্যাশে মুভি: {current_count} টি")
        
        # ৩. নতুন মুভি ফিল্টার (সরাসরি করব, AutoRefresher ব্যবহার না করে)
        new_movies = []
        updated_links = []
        
        # Current movies থেকে keys সেট তৈরি করব
        current_keys = set()
        for movie in current_movies:
            title = movie.get('title', '').lower().strip()
            year = movie.get('year', '').strip()
            quality = movie.get('quality', 'HD').strip()
            blog_source = movie.get('blog_source', 'unknown').strip()
            key = f"{title}|{year}|{quality}|{blog_source}"
            current_keys.add(key)
        
        # নতুন মুভি চেক করব
        for new_movie in new_movies_data:
            title = new_movie.get('title', '').lower().strip()
            year = new_movie.get('year', '').strip()
            quality = new_movie.get('quality', 'HD').strip()
            blog_source = new_movie.get('blog_source', 'unknown').strip()
            new_key = f"{title}|{year}|{quality}|{blog_source}"
            
            if new_key not in current_keys:
                # নতুন মুভি
                new_movies.append(new_movie)
                print(f"   🆕 নতুন: {title} ({year})")
        
        # ৪. ফলাফল প্রসেসিং
        if not new_movies:
            await update.message.reply_text(
                f"ℹ️ কোনো নতুন মুভি পাওয়া যায়নি\n\n"
                f"📊 বর্তমান ক্যাশে মুভি: {current_count} টি\n"
                f"📥 ব্লগারে মোট মুভি: {len(new_movies_data)} টি\n\n"
                f"✅ সব মুভি ইতিমধ্যে ক্যাশে আছে"
            )
            return
        
        # ৫. নতুন মুভি ক্যাশে সেভ করব
        print(f"✅ {len(new_movies)} টি নতুন মুভি পাওয়া গেছে, ক্যাশে সেভ করছি...")
        cache_manager.update_movies(new_movies)
        
        # ৬. চ্যানেলে পোস্ট করব
        success_count = 0
        try:
            from channel_poster import ChannelPoster
            channel_poster = ChannelPoster(cache_manager)
            
            # প্রথম ১০টি মুভি পোস্ট করব (একসাথে অনেকগুলি না)
            for movie in new_movies[:10]:
                try:
                    success = await channel_poster.post_movie_to_channel(movie, context.bot)
                    if success:
                        success_count += 1
                        print(f"   📢 চ্যানেলে পোস্ট করা হয়েছে: {movie['title']}")
                        # প্রতি মুভি পোস্ট করার পর ২ সেকেন্ড অপেক্ষা
                        import asyncio
                        await asyncio.sleep(2)
                except Exception as e:
                    print(f"   ❌ পোস্ট এরর: {e}")
                    continue
        except Exception as e:
            print(f"❌ চ্যানেল পোস্টার এরর: {e}")
            success_count = 0
        
        # ৭. ইউজারকে রিপ্লাই
        success_message = f"""
✅ **রিফ্রেশ সম্পূর্ণ!**

📊 **ফলাফল:**
• ব্লগারে মুভি: {len(new_movies_data)} টি
• নতুন পাওয়া গেছে: {len(new_movies)} টি
• ক্যাশে সেভ করা হয়েছে: {len(new_movies)} টি
• চ্যানেলে পোস্ট করা হয়েছে: {success_count} টি

📈 **আপডেট পর:**
• মোট মুভি: {cache_manager.get_movie_count()} টি

🎬 **প্রথম ৩টি নতুন মুভি:**
"""
        
        for i, movie in enumerate(new_movies[:3], 1):
            success_message += f"{i}. {movie['title']}\n"
        
        if len(new_movies) > 3:
            success_message += f"... এবং আরও {len(new_movies) - 3} টি\n"
        
        success_message += "\n📢 চ্যানেলে নতুন মুভি পোস্ট করা হয়েছে!"
        
        await update.message.reply_text(success_message, parse_mode='Markdown')
        
        print(f"🎯 রিফ্রেশ সম্পূর্ণ: {len(new_movies)} নতুন, {success_count} চ্যানেলে পোস্ট")
        
    except Exception as e:
        print(f"❌ রিফ্রেশ কমান্ড এরর: {e}")
        await update.message.reply_text(f"❌ রিফ্রেশ করতে সমস্যা: {str(e)[:200]}")


async def update_cache_directly(request_data, bot):
    """সরাসরি ক্যাশে আপডেট করবে - আল্ট্রা সিম্পল"""
    try:
        print(f"✅ রিকোয়েস্ট প্রসেসিং: #{request_data['request_id']}")
        
        # ১. রিকোয়েস্ট স্ট্যাটাস আপডেট (এটাই প্রধান কাজ)
        request_manager.mark_fulfilled(request_data['request_id'])
        
        # ২. ছোট ডিলে দেব যাতে ইউজার দেখে বুঝতে পারে
        import asyncio
        await asyncio.sleep(1)
        
        
        
        print(f"✅ রিকোয়েস্ট সম্পূর্ণ: #{request_data['request_id']}")
        return True
        
    except Exception as e:
        print(f"❌ সহজ আপডেট এরর: {e}")
        return False


    
async def request_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """রিকোয়েস্ট কমান্ড হ্যান্ডলার"""
        try:
            user = update.message.from_user
            user_id = user.id
            username = user.username
            full_name = user.first_name
            
            # রিকোয়েস্ট মেসেজ চেক
            if not context.args:
                await update.message.reply_text(
                    "📝 **রিকোয়েস্ট করার ফরম্যাট:**\n\n"
                    "`/request মুভি_নাম বছর`\n"
                    "`/req মুভি_নাম বছর`\n\n"
                    "📌 **উদাহরণ:**\n"
                    "`/request Inception 2010`\n"
                    "`/req Avatar 2009`",
                    parse_mode='Markdown'
                )
                return
            
            movie_query = ' '.join(context.args)
            
            user_display = f"{user.first_name} (@{user.username})" if user.username else user.first_name
            print(f"📨 রিকোয়েস্ট: {user_display} -> '{movie_query}'")
            
            # ১. ইউজার লিমিট চেক
            can_request, remaining = request_manager.check_user_limit(user_id, config.REQUEST_SETTINGS['max_requests_per_day'])
            if not can_request:
                await update.message.reply_text(
                    f"⚠️ **রিকোয়েস্ট লিমিট অতিক্রম!**\n\n"
                    f"📊 আপনি আজ {config.REQUEST_SETTINGS['max_requests_per_day']}টি রিকোয়েস্ট করেছেন\n"
                    f"⏰ পরবর্তী রিকোয়েস্ট: কাল\n\n"
                    f"📞 জরুরি রিকোয়েস্টের জন্য এডমিনের সাথে যোগাযোগ করুন",
                    parse_mode='Markdown'
                )
                return
            
            # ২. ডুপ্লিকেট রিকোয়েস্ট চেক
            is_duplicate, existing_request = request_manager.check_duplicate_request(user_id, movie_query)
            if is_duplicate:
                await update.message.reply_text(
                    f"ℹ️ **এই মুভিটি আগেই রিকোয়েস্ট করেছেন**\n\n"
                    f"🎬 '{existing_request['full_query']}'\n"
                    f"✅ স্ট্যাটাস: {existing_request['status']}\n"
                    f"📅 সময়: {existing_request['request_time'][:10]}\n\n"
                    f"🔍 যদি মুভি থাকে: `/search {existing_request['movie_name']}`",
                    parse_mode='Markdown'
                )
                return
            
            # ৩. প্রথমে ক্যাশে চেক করবে
            await update.message.reply_text(f"🔍 '{movie_query}' ক্যাশে চেক করা হচ্ছে...")
            
            # SearchEngine থেকে exact match চেক
            movies = search_engine.search_movies(movie_query)
            exact_match = False
            
            for movie in movies:
                if movie_query.lower() in movie['title'].lower():
                    exact_match = True
                    # ক্যাশে থাকলে সরাসরি দেখাবে
                    await send_movie_result_with_image(update, movie)
                    return
            
            # ৪. ক্যাশে না থাকলে রিকোয়েস্ট অ্যাড করবে
            if not exact_match:
                request_data = request_manager.add_request(user_id, username, full_name, movie_query)
                
                if request_data:
                    # ইউজারকে কনফার্মেশন
                    await update.message.reply_text(
                        f"❌ **'{movie_query}' আমাদের ডাটাবেজে নেই**\n\n"
                        f"📤 আপনার রিকোয়েস্ট এডমিনের কাছে পাঠানো হয়েছে\n"
                        f"⏳ এডমিন অনলাইন হয়ে মুভিটি আপলোড করবেন\n"
                        f"🔔 আপলোড হওয়ার পর আপনাকে গ্রুপেই জানানো হবে\n\n"
                        f"🎉 ধন্যবাদ! আপনার রিকোয়েস্ট `#{request_data['request_id']}`\n"
                        f"📊 বাকি রিকোয়েস্ট: {remaining} টি",
                        parse_mode='Markdown'
                    )
                    
                    # এডমিনকে নোটিফাই করবে
                    await admin_notifier.notify_admin(request_data, context.bot)
                    
            else:
                await update.message.reply_text("✅ মুভিটি ইতিমধ্যে আছে! উপরের পোস্টটি দেখুন।")
                
        except Exception as e:
            print(f"❌ রিকোয়েস্ট কমান্ড এরর: {e}")
            await update.message.reply_text("❌ রিকোয়েস্ট করতে সমস্যা হয়েছে। পরে চেষ্টা করুন。")

async def my_requests_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ইউজারের রিকোয়েস্ট স্ট্যাটাস দেখাবে"""
        try:
            user = update.message.from_user
            user_requests = request_manager.get_user_requests(user.id)
            
            if not user_requests:
                await update.message.reply_text(
                    "📭 **আপনার কোনো রিকোয়েস্ট নেই**\n\n"
                    "রিকোয়েস্ট করতে: `/request মুভি_নাম বছর`",
                    parse_mode='Markdown'
                )
                return
            
            response = f"📊 **আপনার রিকোয়েস্ট স্ট্যাটাস** ({len(user_requests)} টি)\n\n"
            
            for req in user_requests[:10]:  # সর্বোচ্চ ১০টি
                req_time = datetime.fromisoformat(req['request_time']).strftime("%d/%m %I:%M %p")
                status_emoji = "✅" if req['status'] == 'fulfilled' else "⏳" if req['status'] == 'pending' else "❌"
                
                response += f"{status_emoji} `#{req['request_id']}` - **{req['full_query']}**\n"
                response += f"   📅 {req_time} | 📊 {req['status']}\n\n"
            
            response += "🔍 মুভি সার্চ করতে: `/search মুভি_নাম`"
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            print(f"❌ my_requests কমান্ড এরর: {e}")
            await update.message.reply_text("❌ স্ট্যাটাস দেখাতে সমস্যা হয়েছে。")

async def admin_requests_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """এডমিন রিকোয়েস্ট ড্যাশবোর্ড"""
        try:
            user = update.message.from_user
            
            # শুধু এডমিন দেখতে পারবে
            is_admin = await is_user_admin(update, context)
            if not is_admin and user.id not in config.ADMIN_USER_IDS:
                await update.message.reply_text("⛔ শুধুমাত্র এডমিন এই কমান্ড ব্যবহার করতে পারেন।")
                return
            
            pending_requests = request_manager.get_pending_requests()
            dashboard_text = admin_notifier.create_requests_dashboard(pending_requests)
            
            await update.message.reply_text(dashboard_text, parse_mode='Markdown')
            
        except Exception as e:
            print(f"❌ admin_requests কমান্ড এরর: {e}")
            await update.message.reply_text("❌ ড্যাশবোর্ড দেখাতে সমস্যা হয়েছে。")


async def cleanup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ম্যানুয়াল ক্লিনআপ কমান্ড"""
    try:
        cleaned = request_manager.cleanup_successful_requests(15)
        
        if cleaned > 0:
            await update.message.reply_text(
                f"🧹 {cleaned} টি পুরানো সফল রিকোয়েস্ট ডিলেট করা হয়েছে\n"
                f"⏰ ১৫+ দিন পুরানো সফল রিকোয়েস্ট ডিলেট করা হয়",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "✅ কোনো পুরানো সফল রিকোয়েস্ট নেই\n"
                "ℹ️ শুধু পেন্ডিং এবং ১৫ দিনের মধ্যে সফল রিকোয়েস্ট আছে",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        await update.message.reply_text(f"❌ ক্লিনআপ এরর: {e}")


async def force_refresh_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ফোর্স ক্যাশ রিফ্রেশ কমান্ড"""
    try:
        user = update.message.from_user
        
        # এডমিন চেক (আপনার আইডি = 6723820690)
        if user.id != 6723820690:
            await update.message.reply_text(
                "⛔ এই কমান্ড শুধুমাত্র এডমিন ব্যবহার করতে পারেন।"
            )
            return
        
        # ইউজারকে জানানো
        await update.message.reply_text(
            "🔄 **ফোর্স ক্যাশ রিফ্রেশ শুরু...**\n\n"
            "⚠️ এটি ৩০-৬০ সেকেন্ড সময় নিতে পারে।\n"
            "📊 টার্মিনালে প্রোগ্রেস দেখতে পাবেন..."
        )
        
        print("\n" + "="*60)
        print("🚀 ইউজার ক্যাশ রিফ্রেশ চেয়েছেন:")
        print(f"👤 নাম: {user.first_name}")
        print(f"🆔 আইডি: {user.id}")
        print("="*60)
        
        # ক্যাশ রিফ্রেশ করব
        success, message = cache_manager.force_refresh_cache(blogger_api)
        
        # ইউজারকে রিপ্লাই
        if success:
            await update.message.reply_text(
                f"✅ **ক্যাশ রিফ্রেশ সম্পূর্ণ!**\n\n"
                f"📊 ফলাফল: {message}\n"
                f"🎬 মুভি সংখ্যা: {cache_manager.get_movie_count()} টি\n\n"
                f"🔄 বট এখন নতুন ডাটা নিয়ে কাজ করবে।"
            )
            
            # এডমিনকে প্রাইভেট নোটিফিকেশন
            try:
                await context.bot.send_message(
                    chat_id=user.id,
                    text=f"✅ আপনার ক্যাশ রিফ্রেশ কমান্ড সফল!\n\n"
                         f"📅 সময়: {datetime.now().strftime('%d/%m/%Y %I:%M %p')}\n"
                         f"📊 মুভি: {cache_manager.get_movie_count()} টি\n"
                         f"💾 ফাইল: movies_cache.json"
                )
            except:
                pass
                
        else:
            await update.message.reply_text(
                f"❌ **ক্যাশ রিফ্রেশ ব্যর্থ!**\n\n"
                f"⚠️ সমস্যা: {message}\n\n"
                f"🔧 অনুগ্রহ করে আবার চেষ্টা করুন।"
            )
        
        print(f"🎯 রিফ্রেশ ফলাফল: {'সফল ✅' if success else 'ব্যর্থ ❌'}")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"❌ ফোর্স রিফ্রেশ এরর: {e}")
        await update.message.reply_text(f"❌ কমান্ড এরর: {str(e)[:200]}")


# ========== USER-SPECIFIC BUTTON FUNCTIONS ==========
# এই পুরো ব্লকটা নতুন করে যোগ করো (রিমুভ করার কিছু নেই)

def create_user_specific_keyboard(buttons_data, user_id):
    """
    ইউজার-স্পেসিফিক বাটন তৈরি করে
    buttons_data = [("text1", "action1"), ("text2", "action2")]
    """
    keyboard = []
    for text, action in buttons_data:
        callback_data = f"{action}_{user_id}"
        keyboard.append([InlineKeyboardButton(text, callback_data=callback_data)])
    return InlineKeyboardMarkup(keyboard)


def encode_callback_with_user(callback_data, user_id):
    """ক্যালব্যাক ডাটার সাথে ইউজার আইডি এনকোড করে"""
    return f"{callback_data}_{user_id}"


def extract_user_from_callback(callback_data):
    """ক্যালব্যাক ডাটা থেকে ইউজার আইডি এক্সট্রাক্ট করে"""
    parts = callback_data.split('_')
    try:
        user_id = int(parts[-1])
        original_callback = '_'.join(parts[:-1])
        return original_callback, user_id
    except:
        return callback_data, None



async def handle_movie_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, movie_title, user):
    """ইউজার সাজেশন থেকে মুভি সিলেক্ট করলে"""
    query = update.callback_query
    
    results = local_ai_agent.search_movies(movie_title)
    if results:
        movie = results[0]['movie']
        
        if user_profile_manager:
            user_profile_manager.update_from_search(user.id, movie)
        
        await send_movie_result_with_image(update, movie)
        
        await query.message.edit_text(
            f"✅ @{user.username or user.first_name}, আপনার সিলেক্ট করা মুভি: <b>{movie_title}</b>",
            parse_mode='HTML'
        )


async def send_suggestion_with_confirmation(update, results, original_query):
    """৩টি মুভি কার্ড দেখিয়ে কনফার্মেশন নেয়"""
    user = update.effective_user
    user_id = user.id
    
    # ৩টি কার্ড পাঠাও
    movies_to_show = [item['movie'] for item in results[:3]]
    await send_multiple_movie_cards(update, movies_to_show)
    
    # ইউজার-স্পেসিফিক বাটন তৈরি
    keyboard = [
        [
            InlineKeyboardButton(
                "✅ হ্যাঁ, একটি আছে", 
                callback_data=encode_callback_with_user(f"suggest_yes_{original_query}", user_id)
            )
        ],
        [
            InlineKeyboardButton(
                "❌ না, কোনটিই না", 
                callback_data=encode_callback_with_user(f"suggest_no_{original_query}", user_id)
            )
        ]
    ]
    
    await update.message.reply_text(
        f"❓ @{user.username or user.first_name}, আপনার **'{original_query}'** কি উপরের ৩টির মধ্যে আছে?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# ========== ADMIN ACTION HANDLERS ==========

async def handle_admin_done(update: Update, context: ContextTypes.DEFAULT_TYPE, request_id, admin_user):
    """এডমিন 'Done' ক্লিক করলে"""
    query = update.callback_query
    
    print(f"✅ এডমিন 'Done' ক্লিক করেছেন: {admin_user.first_name} - রিকোয়েস্ট #{request_id}")
    
    request_data = None
    all_requests = request_manager.requests_data.get('requests', [])
    for req in all_requests:
        if req['request_id'] == request_id:
            request_data = req
            break
    
    if not request_data:
        await query.answer("❌ রিকোয়েস্ট ডাটা পাওয়া যায়নি", show_alert=True)
        return
    
    request_manager.mark_fulfilled(request_id)
    
    # এডমিন মেসেজ আপডেট
    await query.edit_message_text(
        f"✅ রিকোয়েস্ট #{request_id} প্রসেস করা হয়েছে!\n\n"
        f"🎬 মুভি: {request_data['full_query']}\n"
        f"👤 ইউজার: @{request_data['username'] if request_data['username'] else 'Unknown'}"
    )
    
    # ইউজারকে নোটিফিকেশন (সঠিক মেনশন সহ)
    try:
        group_id = config.GROUP_ID
        if group_id:
            # ✅ সঠিকভাবে ইউজার মেনশন করা
            if request_data['username']:
                user_mention = f"@{request_data['username']}"
            else:
                user_mention = f"<a href='tg://user?id={request_data['user_id']}'>{request_data['full_name']}</a>"
            
            notification = f"""
{user_mention} 🎉 <b>শুভসংবাদ!</b>

✅ আপনার রিকোয়েস্ট করা <b>{request_data['full_query']}</b> মুভি আপলোড করা হয়েছে!

🔍 <b>এখনই সার্চ করুন:</b> <code>/search {request_data['movie_name']}</code>
"""
            
            await context.bot.send_message(
                chat_id=group_id,
                text=notification,
                parse_mode='HTML'
            )
            print(f"✅ ইউজারকে গ্রুপে নোটিফাই করা হয়েছে: {request_data['user_id']}")
    except Exception as e:
        print(f"❌ ইউজার নোটিফিকেশন এরর: {e}")


async def handle_admin_later(update: Update, context: ContextTypes.DEFAULT_TYPE, request_id, admin_user):
    """এডমিন 'Later' ক্লিক করলে"""
    query = update.callback_query
    
    await query.edit_message_text(
        query.message.text + "\n\n⏳ পরে দেখা হবে।",
        reply_markup=None
    )
    await query.answer(f"রিকোয়েস্ট #{request_id} পরে দেখা হবে")


async def handle_admin_reject(update: Update, context: ContextTypes.DEFAULT_TYPE, request_id, admin_user):
    """এডমিন 'Reject' ক্লিক করলে"""
    query = update.callback_query
    
    # রিকোয়েস্ট ডাটা খুঁজে বের করো
    request_data = None
    all_requests = request_manager.requests_data.get('requests', [])
    for req in all_requests:
        if req['request_id'] == request_id:
            request_data = req
            break
    
    if not request_data:
        await query.answer("❌ রিকোয়েস্ট ডাটা পাওয়া যায়নি", show_alert=True)
        return
    
    # স্ট্যাটাস আপডেট (রিজেক্ট)
    if hasattr(request_manager, 'mark_rejected'):
        request_manager.mark_rejected(request_id)
    
    # এডমিনকে কনফার্মেশন
    await query.edit_message_text(
        f"❌ রিকোয়েস্ট `#{request_id}` রিজেক্ট করা হয়েছে।",
        parse_mode='Markdown'
    )
    
    # ইউজারকে জানাও
    try:
        group_id = config.GROUP_ID
        if group_id:
            user_mention = f"@{request_data['username']}" if request_data['username'] else request_data['full_name']
            
            notification = f"""
{user_mention} 😔 আপনার রিকোয়েস্ট করা **{request_data['full_query']}** বর্তমানে আপলোড করা সম্ভব নয়।

কারণ: এডমিন কর্তৃক রিজেক্ট করা হয়েছে।
"""
            
            await context.bot.send_message(
                chat_id=group_id,
                text=notification,
                parse_mode='Markdown'
            )
            print(f"✅ ইউজারকে রিজেক্ট নোটিফিকেশন পাঠানো হয়েছে")
    except Exception as e:
        print(f"❌ ইউজার নোটিফিকেশন এরর: {e}")
    
    await query.answer("❌ রিজেক্ট করা হয়েছে")


async def ask_confirmation_after_cards(update: Update, original_query, matched_movies):
    """৩টি কার্ড দেখানোর পর কনফার্মেশন জিজ্ঞাসা করে"""
    user = update.effective_user
    user_mention = f"@{user.username}" if user.username else user.first_name
    
    # বাটন তৈরি
    keyboard = [
        [
            InlineKeyboardButton(
                "✅ হ্যাঁ, একটি আছে", 
                callback_data=encode_callback_with_user(f"confirm_yes_{original_query}", user.id)
            )
        ],
        [
            InlineKeyboardButton(
                "❌ না, কোনটিই না", 
                callback_data=encode_callback_with_user(f"confirm_no_{original_query}", user.id)
            )
        ]
    ]
    
    # মেসেজ তৈরি (HTML ফরম্যাট)
    message = f"❓ {user_mention}, আপনার '<b>{original_query}</b>' কি উপরের ৩টির মধ্যে আছে?"
    
    await update.message.reply_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def handle_confirmation_yes(update: Update, context: ContextTypes.DEFAULT_TYPE, original_query):
    """ইউজার বলেছে হ্যাঁ, একটি আছে - শুধু নোটিফিকেশন দেয়"""
    query = update.callback_query
    user = query.from_user
    
    await query.message.edit_text(
        f"👍 @{user.username or user.first_name}, উপরের মুভিগুলোর মধ্যে আপনারটি সিলেক্ট করুন।",
        parse_mode='Markdown'
    )
    
    # শুধু নোটিফিকেশন দাও, কোনো কার্ড নয়
    await query.answer("✅ উপরের মুভিগুলোর মধ্যে আপনারটি সিলেক্ট করুন")


async def handle_confirmation_no(update: Update, context: ContextTypes.DEFAULT_TYPE, original_query, user):
    """ইউজার বলেছে কোনটিই না → রিকোয়েস্ট নাও"""
    query = update.callback_query
    
    # ✅ ডুপ্লিকেট চেক
    is_duplicate, existing = request_manager.check_duplicate_request(user.id, original_query)
    
    if is_duplicate:
        # স্ট্যাটাস অনুযায়ী ইমোজি
        status_emoji = "✅" if existing['status'] == 'fulfilled' else "⏳" if existing['status'] == 'pending' else "❌"
        
        await query.message.edit_text(
            f"ℹ️ @{user.username or user.first_name}, আপনি ইতিমধ্যে '<b>{original_query}</b>' রিকোয়েস্ট করেছেন!\n\n"
            f"{status_emoji} <b>স্ট্যাটাস:</b> {existing['status']}\n"
            f"🆔 <b>রিকোয়েস্ট আইডি:</b> #{existing['request_id']}\n"
            f"📅 <b>সময়:</b> {existing['request_time'][:10]}",
            parse_mode='HTML'
        )
        await query.answer("✅ ইতিমধ্যে রিকোয়েস্ট করা হয়েছে")
        return
    
    # নতুন রিকোয়েস্ট
    request_data = request_manager.add_request(
        user_id=user.id,
        username=user.username,
        full_name=user.first_name,
        movie_query=original_query
    )
    
    if request_data:
        await query.message.edit_text(
            f"📨 @{user.username or user.first_name}, আপনার '<b>{original_query}</b>' রিকোয়েস্ট নেওয়া হয়েছে.\n\n"
            f"🆔 <b>রিকোয়েস্ট আইডি:</b> #{request_data['request_id']}\n"
            f"⏳ <b>স্ট্যাটাস:</b> পেন্ডিং\n\n"
            f"👑 এডমিনকে জানানো হয়েছে. আপলোড হলে জানিয়ে দেব.",
            parse_mode='HTML'
        )
        
        await admin_notifier.notify_admin_with_buttons(request_data, context.bot)
    else:
        await query.message.edit_text("❌ রিকোয়েস্ট নিতে সমস্যা হয়েছে। পরে চেষ্টা করুন।")
    

# ================== MAIN FUNCTION (ONLY WEBHOOK FOR RENDER) ==================
def main():
    """Render-এর জন্য শুধু Webhook মোডে বট চালাবে"""
    print("🤖 বট শুরু হচ্ছে...")
    
    # সার্ভিসেস ইনিশিয়ালাইজ
    initialize_services()
    
    # বট অ্যাপ্লিকেশন তৈরি
    app = Application.builder().token(config.BOT_TOKEN).build()
    
    # ========== সব হ্যান্ডলার এখানে যোগ করুন ==========
    # কমান্ড হ্যান্ডলার
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CommandHandler("testimage", test_image_system))
    app.add_handler(CommandHandler("refresh_status", refresh_status_command))
    app.add_handler(CommandHandler("refresh", refresh_command))
    app.add_handler(CommandHandler("request", request_command))
    app.add_handler(CommandHandler("req", request_command))
    app.add_handler(CommandHandler("myrequests", my_requests_command))
    app.add_handler(CommandHandler("status", my_requests_command))
    app.add_handler(CommandHandler("requests", admin_requests_dashboard))
    app.add_handler(CommandHandler("cleanup", cleanup_command))
    app.add_handler(CommandHandler("force_refresh", force_refresh_command))
    app.add_handler(CommandHandler("bulk_post", bulk_post_command))
    app.add_handler(CommandHandler("confirm_bulk_post", confirm_bulk_post_command))
    app.add_handler(CommandHandler("cancel", cancel_bulk_post_command))
    
    # ক্যালব্যাক হ্যান্ডলার
    app.add_handler(CallbackQueryHandler(button_callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^(🤖 এডমিন কমান্ড লিস্ট|📊 ক্যাশ স্ট্যাটাস|🔄 রিফ্রেশ)$'), handle_admin_button))
    
    # গ্রুপে নতুন মেম্বার ওয়েলকাম
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(ChatMemberHandler(handle_chat_member_update, ChatMemberHandler.CHAT_MEMBER))
    
    # মেসেজ হ্যান্ডলার (সবশেষে)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # এরর হ্যান্ডলার
    app.add_error_handler(error_handler)
    
    # ========== শুধু ওয়েবহুক মোড (Render-এর জন্য) ==========
    PORT = int(os.environ.get('PORT', 10000))
    webhook_url = f"https://movie-bot-bg7m.onrender.com/{config.BOT_TOKEN}"
    
    print(f"🌐 Webhook URL: {webhook_url}")
    print(f"🔧 Using PORT: {PORT}")
    
    # ওয়েবহুক চালানোর ফাংশন (পোলিং-এর কোনো উল্লেখ নেই)
    async def run_webhook():
        # ১. আগের কোনো ওয়েবহুক ডিলিট করে শুরু
        await app.bot.delete_webhook(drop_pending_updates=True)
        # ২. নতুন ওয়েবহুক সেট
        await app.bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query", "chat_member"]
        )
        print("✅ Webhook সেট করা হয়েছে")
        
        # ৩. ওয়েবহুক সার্ভার শুরু
        await app.updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=config.BOT_TOKEN,
            webhook_url=webhook_url,
            drop_pending_updates=True
        )
        print("✅ Webhook সার্ভার চলছে")
        
        # ৪. বট চালু রাখতে infinite wait
        await asyncio.Event().wait()
    
    # চালানো
    try:
        asyncio.run(run_webhook())
    except KeyboardInterrupt:
        print("🛑 বট বন্ধ করা হচ্ছে")
    except Exception as e:
        print(f"❌ Webhook মোডে ব্যর্থ: {e}")


if __name__ == "__main__":
    main()
