# admin_notifier.py - এডমিন নোটিফিকেশন সিস্টেট
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime

class AdminNotifier:
    def __init__(self, admin_user_ids, notification_channel_id=None):
        self.admin_user_ids = admin_user_ids
        self.notification_channel_id = notification_channel_id
    
    async def notify_admin(self, request_data, bot):
        """এডমিনকে রিকোয়েস্ট নোটিফাই করবে"""
        try:
            request_id = request_data['request_id']
            movie_name = request_data['movie_name']
            movie_year = request_data['movie_year']
            username = request_data['username']
            full_name = request_data['full_name']
            user_id = request_data['user_id']
            
            # নোটিফিকেশন মেসেজ তৈরি
            notification_text = f"""
🚨 **নতুন মুভি রিকোয়েস্ট** 🚨

🎬 মুভি: "{movie_name} {movie_year}"
👤 ইউজার: {full_name} (@{username})
🆔 ইউজার ID: `{user_id}`
📅 রিকোয়েস্ট সময়: {datetime.now().strftime("%d %b %Y, %I:%M %p")}
🔢 রিকোয়েস্ট ID: `#{request_id}`

🔍 **সার্চ করতে:** `{movie_name} {movie_year}`
            """
            
            # "Done ✅" বাটন সহ কীবোর্ড
            keyboard = [
                [
                    InlineKeyboardButton("✅ Done", callback_data=f"req_done_{request_id}"),
                    InlineKeyboardButton("⏳ Later", callback_data=f"req_later_{request_id}")
                ],
                [
                    InlineKeyboardButton("❌ Reject", callback_data=f"req_reject_{request_id}")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # সব এডমিনকে নোটিফাই করবে
            for admin_id in self.admin_user_ids:
                try:
                    await bot.send_message(
                        chat_id=admin_id,
                        text=notification_text,
                        parse_mode='HTML',
                        reply_markup=reply_markup
                    )
                    print(f"✅ এডমিনকে নোটিফাই করা হয়েছে: {admin_id}")
                except Exception as e:
                    print(f"❌ এডমিন নোটিফিকেশন এরর: {e}")
            
            # চ্যানেলে নোটিফাই করবে (যদি থাকে)
            if self.notification_channel_id:
                try:
                    await bot.send_message(
                        chat_id=self.notification_channel_id,
                        text=notification_text,
                        parse_mode='Markdown',
                        reply_markup=reply_markup
                    )
                except Exception as e:
                    print(f"❌ চ্যানেল নোটিফিকেশন এরর: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ এডমিন নোটিফিকেশন এরর: {e}")
            return False
    
    async def notify_user_fulfilled(self, request_data, bot, group_id=None):
        """ইউজারকে নোটিফাই করবে যখন মুভি আপলোড হবে"""
        try:
            request_id = request_data['request_id']
            movie_name = request_data['movie_name']
            movie_year = request_data['movie_year']
            username = request_data['username']
            user_id = request_data['user_id']
            
            # ইউজারনেম চেক
            user_mention = f"@{username}" if username and username != f"user_{user_id}" else f"[ইউজার](tg://user?id={user_id})"
            
            user_notification = f"""
{user_mention} 🎉 **শুভসংবাদ!**

✅ আপনার রিকোয়েস্ট করা মুভি আপলোড করা হয়েছে!

🎬 **{movie_name} {movie_year}**
📅 রিকোয়েস্ট সময়: {datetime.fromisoformat(request_data['request_time']).strftime("%d %b %I:%M %p")}
✅ আপডেট: {datetime.now().strftime("%d %b %I:%M %p")}

🔍 **এখনই দেখুন:**
`/search {movie_name}`
অথবা সরাসরি: `{movie_name}`

👇 ক্লিক করে কপি করুন এবং সার্চ করুন!
            """
            
            # গ্রুপে নোটিফাই করবে (ইউজার মেনশন সহ)
            if group_id:
                try:
                    await bot.send_message(
                        chat_id=group_id,
                        text=user_notification,
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
                    print(f"✅ ইউজারকে গ্রুপে নোটিফাই করা হয়েছে")
                    return True
                except Exception as e:
                    print(f"❌ গ্রুপ নোটিফিকেশন এরর: {e}")
                    # গ্রুপে পাঠানো না গেলে ইউজারকে প্রাইভেটে পাঠাবে
                    pass
            
            # ইউজারকে প্রাইভেটে নোটিফাই করবে
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=f"✅ আপনার রিকোয়েস্ট #{request_id} সম্পূর্ণ হয়েছে!\n\n🎬 {movie_name} {movie_year} এখন সার্চ করে দেখতে পারেন।\n\n🔍 সার্চ করুন: `/search {movie_name}`",
                    parse_mode='Markdown'
                )
                print(f"✅ ইউজারকে প্রাইভেটে নোটিফাই করা হয়েছে: {user_id}")
                return True
            except Exception as e:
                print(f"❌ প্রাইভেট নোটিফিকেশন এরর: {e}")
                return False
        
        except Exception as e:
            print(f"❌ ইউজার নোটিফিকেশন এরর: {e}")
            return False
    
    def create_requests_dashboard(self, pending_requests):
        """এডমিন ড্যাশবোর্ড তৈরি করবে"""
        if not pending_requests:
            return "📭 **কোনো পেন্ডিং রিকোয়েস্ট নেই**\n\nসব রিকোয়েস্ট প্রসেস করা হয়েছে।"
        
        dashboard_text = f"📋 **পেন্ডিং রিকোয়েস্ট** ({len(pending_requests)} টি)\n\n"
        
        for i, req in enumerate(pending_requests[:10], 1):  # প্রথম ১০টি
            req_time = datetime.fromisoformat(req['request_time']).strftime("%d/%m %I:%M %p")
            dashboard_text += f"{i}. `#{req['request_id']}` - **{req['movie_name']} {req['movie_year']}**\n"
            dashboard_text += f"   👤 {req['full_name']} | ⏰ {req_time}\n\n"
        
        if len(pending_requests) > 10:
            dashboard_text += f"... এবং আরও {len(pending_requests) - 10} টি\n"
        
        dashboard_text += "\n📊 **স্ট্যাটিস্টিক্স:**\n"
        dashboard_text += "• পেন্ডিং রিকোয়েস্ট: {} টি\n".format(len(pending_requests))
        
        return dashboard_text