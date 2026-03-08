# admin_notifier.py - এডমিন নোটিফিকেশন সিস্টেম
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime

class AdminNotifier:
    def __init__(self, admin_user_ids, notification_channel_id=None):
        self.admin_user_ids = admin_user_ids
        self.notification_channel_id = notification_channel_id
    
    async def notify_admin(self, request_data, bot):
        """এডমিনকে রিকোয়েস্ট নোটিফাই করবে (পুরনো ভার্সন)"""
        return await self.notify_admin_with_buttons(request_data, bot)
    
    async def notify_admin_with_buttons(self, request_data, bot):
        """এডমিনকে রিকোয়েস্ট নোটিফাই করবে - এডমিন-অনলি বাটন সহ"""
        try:
            request_id = request_data['request_id']
            movie_name = request_data['movie_name']
            movie_year = request_data['movie_year']
            username = request_data['username']
            full_name = request_data['full_name']
            user_id = request_data['user_id']
            
            # নোটিফিকেশন মেসেজ তৈরি (HTML ফরম্যাট)
            notification_text = f"""
    🚨 <b>নতুন মুভি রিকোয়েস্ট</b> 🚨

    🎬 <b>মুভি:</b> "{movie_name} {movie_year}"
    👤 <b>ইউজার:</b> {full_name} (@{username})
    🆔 <b>ইউজার ID:</b> <code>{user_id}</code>
    📅 <b>রিকোয়েস্ট সময়:</b> {datetime.now().strftime("%d %b %Y, %I:%M %p")}
    🔢 <b>রিকোয়েস্ট ID:</b> <code>#{request_id}</code>

    🔍 <b>সার্চ করতে:</b> <code>{movie_name} {movie_year}</code>
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
                        parse_mode='HTML',
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
            
            # ইউজারনেম চেক (HTML ফরম্যাট)
            if username and username != f"user_{user_id}":
                user_mention = f"@{username}"
            else:
                user_mention = f"<a href='tg://user?id={user_id}'>ইউজার</a>"
            
            user_notification = f"""
    {user_mention} 🎉 <b>শুভসংবাদ!</b>

    ✅ আপনার রিকোয়েস্ট করা মুভি আপলোড করা হয়েছে!

    🎬 <b>{movie_name} {movie_year}</b>
    📅 <b>রিকোয়েস্ট সময়:</b> {datetime.fromisoformat(request_data['request_time']).strftime("%d %b %I:%M %p")}
    ✅ <b>আপডেট:</b> {datetime.now().strftime("%d %b %I:%M %p")}

    🔍 <b>এখনই দেখুন:</b>
    <code>/search {movie_name}</code>
    অথবা সরাসরি: <code>{movie_name}</code>

    👇 ক্লিক করে কপি করুন এবং সার্চ করুন!
            """
            
            # গ্রুপে নোটিফাই করবে (ইউজার মেনশন সহ)
            if group_id:
                try:
                    await bot.send_message(
                        chat_id=group_id,
                        text=user_notification,
                        parse_mode='HTML',
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
                    text=f"✅ আপনার রিকোয়েস্ট #{request_id} সম্পূর্ণ হয়েছে!\n\n🎬 <b>{movie_name} {movie_year}</b> এখন সার্চ করে দেখতে পারেন।\n\n🔍 <b>সার্চ করুন:</b> <code>/search {movie_name}</code>",
                    parse_mode='HTML'
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