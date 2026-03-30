# short_admin_menu.py - আপডেটেড ভার্সন
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

class ShortAdminMenu:
    def __init__(self):
        self.commands_info = {
            '/force_refresh': '🧹 পুরো ক্যাশ ডিলিট করে নতুন তৈরি করে',
            '/refresh': '🔄 শুধু নতুন মুভি খোঁজে এবং যোগ করে',
            '/cache_status': '📊 ক্যাশের মুভি সংখ্যা ও আপডেট সময় দেখায়',
            '/refresh_status': '⏰ অটো রিফ্রেশার স্ট্যাটাস দেখায়',
            '/cleanup': '🗑️ ১৫+ দিন পুরানো সফল রিকোয়েস্ট ডিলিট করে',
            '/bulk_post': '📢 নতুন চ্যানেলে সব মুভি পোস্ট করে (বাল্ক পোস্টিং)',
            '/start': '🚀 বট ওয়েলকাম মেসেজ ও মেনু দেখায়'
        }
    
    def create_fixed_admin_keyboard(self):
        """ফিক্সড এডমিন কীবোর্ড"""
        keyboard = [
            [KeyboardButton("🤖 এডমিন কমান্ড লিস্ট")],
            [KeyboardButton("📊 ক্যাশ স্ট্যাটাস"), KeyboardButton("🔄 রিফ্রেশ")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
    
    def remove_keyboard(self):
        """কীবোর্ড হাইড করার জন্য"""
        from telegram import ReplyKeyboardRemove
        return ReplyKeyboardRemove()
    
    def get_commands_list_text(self):
        """কমান্ড লিস্ট টেক্সট"""
        text = "🤖 <b>এডমিন কমান্ড লিস্ট</b>\n\n"
        for cmd, desc in self.commands_info.items():
            text += f"• <code>{cmd}</code> - {desc}\n"
        text += "\n📝 <i>কমান্ড টাইপ করুন অথবা উপরের বাটন ব্যবহার করুন</i>"
        return text
    
    def create_inline_commands_keyboard(self):
        """ইনলাইন কীবোর্ড (কমান্ড সিলেক্ট করার জন্য)"""
        keyboard = []
        row = []
        for i, cmd in enumerate(self.commands_info.keys()):
            if i % 2 == 0 and i > 0:
                keyboard.append(row)
                row = []
            emoji_map = {
                '/force_refresh': '🧹',
                '/refresh': '🔄', 
                '/cache_status': '📊',
                '/refresh_status': '⏰',
                '/cleanup': '🗑️',
                '/bulk_post': '📢',
                '/start': '🚀'
            }
            emoji = emoji_map.get(cmd, '🔹')
            display_text = cmd.replace('/', '')
            row.append(InlineKeyboardButton(
                f"{emoji}{display_text}", 
                callback_data=f"run_{cmd[1:]}"
            ))
        if row:
            keyboard.append(row)
        return InlineKeyboardMarkup(keyboard)