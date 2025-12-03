# auto_refresher.py - ফিক্সড ভার্সন
import asyncio
import logging
from datetime import datetime


class AutoRefresher:
    def __init__(self, blogger_api, cache_manager, search_engine, request_manager=None):
        self.blogger_api = blogger_api
        self.cache_manager = cache_manager
        self.search_engine = search_engine
        self.request_manager = request_manager
        self.is_running = False
        self.refresh_interval = 30 * 60
        self.bot_app = None
        self.admin_dashboard_ids = {}  # ✅ নতুন: {admin_id: message_id}

    async def start_auto_refresh(self, app):
        """অটো রিফ্রেশ শুরু করবে"""
        self.is_running = True
        self.app = app  # ✅ এই লাইন নিশ্চিত করুন
        
        print("🔄 অটো রিফ্রেশার শুরু হয়েছে")
        
        # ✅ বট রেফারেন্স পাস করুন
        if hasattr(self, 'bot_app'):
            self.bot_app = app
            print(f"✅ বট রেফারেন্স সেট করা হয়েছে")
        
        while self.is_running:
            try:
                await self.check_for_new_posts()
                print(f"⏰ পরবর্তী চেক: {self.refresh_interval//60} মিনিট পর")
                await asyncio.sleep(self.refresh_interval)
            except Exception as e:
                print(f"❌ অটো রিফ্রেশ এরর: {e}")
                await asyncio.sleep(60)

    async def check_for_new_posts(self):
        """সব ব্লগার থেকে নতুন পোস্ট চেক করবে"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n🔄 [{current_time}] অটো রিফ্রেশ শুরু...")

        # ✅ বট রেফারেন্স চেক
        if not hasattr(self, 'bot_app') or not self.bot_app:
            print("⚠️ বট রেফারেন্স নেই, শুধু চেক করব...")
        
        # বর্তমান ক্যাশড মুভি
        current_movies = self.cache_manager.get_all_movies()
        current_count = len(current_movies)
        print(f"📊 বর্তমান ক্যাশে মুভি: {current_count} টি")
        
        # সব ব্লগার থেকে নতুন ডাটা fetch
        new_movies_data = self.blogger_api.get_all_posts_from_all_blogs()
        
        if not new_movies_data:
            print("❌ ব্লগার থেকে কোনো ডাটা পাওয়া যায়নি")
            # শুধু ড্যাশবোর্ড আপডেট করব (কোনো নতুন মুভি নেই)
            await self.update_admin_dashboard(0, 0, [], [])
            return
        
        print(f"📥 ব্লগারে মোট মুভি: {len(new_movies_data)} টি")
        
        # স্মার্ট ডুপ্লিকেট চেক সহ নতুন মুভি ফিল্টার + লিংক আপডেট ডিটেক্ট
        new_movies, updated_links = self.filter_new_movies(new_movies_data, current_movies)
        
        # লিংক আপডেট করা মুভিগুলোর চ্যানেল পোস্ট আপডেট
        if updated_links:
            print(f"📢 {len(updated_links)} টি মুভির লিংক আপডেট হয়েছে, চ্যানেল আপডেট করছি...")
            
            try:
                from channel_poster import ChannelPoster
                channel_poster = ChannelPoster(self.cache_manager)
                
                for updated in updated_links:
                    success = await channel_poster.update_movie_post(updated['title'], self.bot_app.bot)
                    if success:
                        print(f"   ✅ চ্যানেল পোস্ট আপডেট করা হয়েছে: {updated['title']}")
            except Exception as e:
                print(f"❌ চ্যানেল আপডেট করতে সমস্যা: {e}")
        
        if new_movies:
            # নতুন মুভি ক্যাশে অ্যাড করবে
            success = self.cache_manager.update_movies(new_movies)
            if success:
                print(f"✅ {len(new_movies)} টি নতুন মুভি ক্যাশে অ্যাড করা হয়েছে")
                
                # নতুন মুভি চ্যানেলে পোস্ট করবে
                try:
                    if hasattr(self, 'bot_app') and self.bot_app:
                        from channel_poster import ChannelPoster
                        channel_poster = ChannelPoster(self.cache_manager)
                        success_count = await channel_poster.post_multiple_movies(new_movies, self.bot_app.bot)
                        print(f"📢 চ্যানেলে নতুন পোস্ট করা হয়েছে: {success_count} টি মুভি")
                except Exception as e:
                    print(f"❌ চ্যানেলে পোস্ট করতে সমস্যা: {e}")
        else:
            print("ℹ️ কোনো নতুন মুভি পাওয়া যায়নি")
        
        # ✅ এডমিন ড্যাশবোর্ড আপডেট করব (গ্রুপে নোটিফিকেশন নেই)
        await self.update_admin_dashboard(
            len(new_movies), 
            len(updated_links), 
            new_movies[:3],  # প্রথম ৩টি
            updated_links[:3]  # প্রথম ৩টি
        )
        
        updated_count = self.cache_manager.get_movie_count()
        print(f"📈 আপডেট后 ক্যাশে মুভি: {updated_count} টি")
    
    def filter_new_movies(self, new_movies_data, current_movies):
        """স্মার্ট ডুপ্লিকেট চেক + লিংক আপডেট ডিটেক্ট করবে"""
        new_movies = []
        updated_links = []
        
        # Current movies-কে dict-এ কনভার্ট করবে (title->movie)
        current_movies_dict = {}
        for movie in current_movies:
            current_movies_dict[movie['title'].lower()] = movie
        
        for new_movie in new_movies_data:
            title_lower = new_movie['title'].lower()
            
            if title_lower not in current_movies_dict:
                # সম্পূর্ণ নতুন মুভি
                new_movies.append(new_movie)
                print(f"   🆕 নতুন মুভি: {new_movie['title']}")
            else:
                # Existing মুভি - লিংক আপডেট চেক করবে
                existing_movie = current_movies_dict[title_lower]
                new_link = new_movie.get('detail_link')
                old_link = existing_movie.get('detail_link')
                
                if new_link and (not old_link or new_link != old_link):
                    # লিংক আপডেট হয়েছে
                    updated_links.append({
                        'title': new_movie['title'],
                        'old_link': old_link,
                        'new_link': new_link,
                        'movie_data': new_movie
                    })
                    print(f"   🔄 লিংক আপডেট: {new_movie['title']}")
                    print(f"      পুরানো: {old_link[:50] if old_link else 'NONE'}")
                    print(f"      নতুন: {new_link[:50]}")
                    
                    # ক্যাশে আপডেট করবে
                    self.cache_manager.update_movie_link(new_movie['title'], new_link)
        
        if updated_links:
            print(f"✅ {len(updated_links)} টি মুভির লিংক আপডেট হয়েছে")
        
        return new_movies, updated_links
    
    async def update_admin_dashboard(self, new_movies_count=0, updated_links_count=0, new_movies=None, updated_links=None):
        """এডমিন ড্যাশবোর্ড আপডেট করবে"""
        try:
            if not hasattr(self, 'bot_app') or not self.bot_app:
                print("⚠️ বট রেফারেন্স নেই, ড্যাশবোর্ড আপডেট করা যাচ্ছে না")
                return False
            
            import config
            from datetime import datetime
            
            current_time = datetime.now().strftime("%d %b %Y, %I:%M %p")
            
            # ড্যাশবোর্ড মেসেজ তৈরি
            dashboard_text = f"""
🤖 <b>বট আপডেট ড্যাশবোর্ড</b>

⏰ <b>লাস্ট আপডেট:</b> {current_time}
🔄 <b>টাইপ:</b> {'নতুন মুভি' if new_movies_count > 0 else 'রেগুলার চেক'}
📊 <b>মোট মুভি:</b> {self.cache_manager.get_movie_count()} টি

"""
            
            if new_movies_count > 0:
                dashboard_text += f"✅ <b>নতুন মুভি:</b> {new_movies_count} টি\n"
                if new_movies:
                    for movie in new_movies[:2]:  # প্রথম ২টি
                        dashboard_text += f"   • {movie['title']}\n"
                    if new_movies_count > 2:
                        dashboard_text += f"   ... এবং আরও {new_movies_count - 2} টি\n"
            
            if updated_links_count > 0:
                dashboard_text += f"\n🔗 <b>লিংক আপডেট:</b> {updated_links_count} টি\n"
            
            dashboard_text += f"\n📅 <b>পরবর্তী চেক:</b> ৩০ মিনিট পর"
            dashboard_text += f"\n⚡ <b>বট স্ট্যাটাস:</b> সক্রিয় ✅"
            
            # সব এডমিনের জন্য ড্যাশবোর্ড আপডেট করব
            success_count = 0
            for admin_id in config.ADMIN_USER_IDS:
                try:
                    if admin_id in self.admin_dashboard_ids:
                        # আগের মেসেজ এডিট করব
                        await self.bot_app.bot.edit_message_text(
                            chat_id=admin_id,
                            message_id=self.admin_dashboard_ids[admin_id],
                            text=dashboard_text,
                            parse_mode='HTML'
                        )
                        print(f"✅ এডমিন ড্যাশবোর্ড আপডেট হয়েছে: {admin_id}")
                    else:
                        # নতুন ড্যাশবোর্ড মেসেজ তৈরি করব
                        message = await self.bot_app.bot.send_message(
                            chat_id=admin_id,
                            text=dashboard_text,
                            parse_mode='HTML'
                        )
                        self.admin_dashboard_ids[admin_id] = message.message_id
                        print(f"📊 নতুন ড্যাশবোর্ড তৈরি হয়েছে: {admin_id}")
                    
                    success_count += 1
                    
                except Exception as e:
                    error_msg = str(e)
                    if "message to edit not found" in error_msg or "message not found" in error_msg:
                        # মেসেজ নাই, নতুন তৈরি করব
                        try:
                            message = await self.bot_app.bot.send_message(
                                chat_id=admin_id,
                                text=dashboard_text,
                                parse_mode='HTML'
                            )
                            self.admin_dashboard_ids[admin_id] = message.message_id
                            print(f"🔄 ড্যাশবোর্ড রিক্রিয়েট হয়েছে: {admin_id}")
                            success_count += 1
                        except Exception as e2:
                            print(f"❌ ড্যাশবোর্ড রিক্রিয়েট ব্যর্থ: {admin_id} - {e2}")
                    else:
                        print(f"❌ ড্যাশবোর্ড আপডেট এরর: {admin_id} - {e}")
            
            print(f"📊 ড্যাশবোর্ড আপডেট সম্পূর্ণ: {success_count}/{len(config.ADMIN_USER_IDS)} জন এডমিন")
            return success_count > 0
            
        except Exception as e:
            print(f"❌ ড্যাশবোর্ড সিস্টেম এরর: {e}")
            return False

    def stop_auto_refresh(self):
        """অটো রিফ্রেশ বন্ধ করবে"""
        self.is_running = False
        print("🛑 অটো রিফ্রেশার বন্ধ করা হয়েছে")