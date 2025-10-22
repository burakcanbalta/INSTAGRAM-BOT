from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import json
import logging
from logging.handlers import RotatingFileHandler
import sqlite3
import os
from datetime import datetime, timedelta
import argparse

class InstagramBot:
    def __init__(self, config_file="config.json"):
        self.config = self.load_config(config_file)
        self.setup_logging()
        self.init_database()
        self.driver = None
        self.wait = None
        self.is_logged_in = False

    def load_config(self, config_file):
        default_config = {
            "browser": {
                "headless": False,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            },
            "limits": {
                "daily_follows": 150,
                "daily_likes": 300,
                "daily_comments": 50,
                "hourly_actions": 30
            },
            "timing": {
                "min_delay": 2,
                "max_delay": 5,
                "between_actions": 10
            },
            "targeting": {
                "hashtags": ["python", "programming", "coding", "developer"],
                "locations": [],
                "competitors": []
            }
        }

        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                RotatingFileHandler('instagram_bot.log', maxBytes=10485760, backupCount=5),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def init_database(self):
        conn = sqlite3.connect('instagram_bot.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type TEXT,
                target TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                follows INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                unfollows INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS followed_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                followed_at DATETIME,
                unfollow_after_days INTEGER DEFAULT 3
            )
        ''')
        
        conn.commit()
        conn.close()

    def setup_driver(self):
        chrome_options = Options()
        
        if self.config['browser']['headless']:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument(f'--user-agent={self.config["browser"]["user_agent"]}')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.wait = WebDriverWait(self.driver, 10)
        self.logger.info("Browser başlatıldı")

    def random_delay(self):
        delay = random.uniform(self.config['timing']['min_delay'], self.config['timing']['max_delay'])
        time.sleep(delay)

    def login(self, username, password):
        try:
            self.logger.info("Instagram'a giriş yapılıyor...")
            self.driver.get("https://www.instagram.com/accounts/login/")
            
            self.random_delay()
            
            username_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_input.send_keys(username)
            
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.send_keys(password)
            password_input.send_keys(Keys.RETURN)
            
            self.random_delay()
            
            # "Şimdi Değil" butonunu atla
            try:
                not_now_btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Şimdi Değil')]"))
                )
                not_now_btn.click()
                self.random_delay()
            except TimeoutException:
                pass
            
            # Bildirimleri kapat
            try:
                not_now_notif = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Şimdi Değil')]"))
                )
                not_now_notif.click()
            except TimeoutException:
                pass
            
            self.is_logged_in = True
            self.logger.info("Başarıyla giriş yapıldı")
            return True
            
        except Exception as e:
            self.logger.error(f"Giriş hatası: {e}")
            return False

    def log_activity(self, action_type, target, success=True):
        conn = sqlite3.connect('instagram_bot.db')
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO activity_log (action_type, target, success) VALUES (?, ?, ?)',
            (action_type, target, success)
        )
        conn.commit()
        conn.close()

    def get_today_stats(self):
        conn = sqlite3.connect('instagram_bot.db')
        cursor = conn.cursor()
        today = datetime.now().date()
        
        cursor.execute(
            'SELECT follows, likes, comments, unfollows FROM daily_stats WHERE date = ?',
            (today,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'follows': result[0],
                'likes': result[1],
                'comments': result[2],
                'unfollows': result[3]
            }
        else:
            return {'follows': 0, 'likes': 0, 'comments': 0, 'unfollows': 0}

    def update_daily_stats(self, action_type):
        conn = sqlite3.connect('instagram_bot.db')
        cursor = conn.cursor()
        today = datetime.now().date()
        
        cursor.execute(
            'SELECT id FROM daily_stats WHERE date = ?',
            (today,)
        )
        result = cursor.fetchone()
        
        if result:
            cursor.execute(
                f'UPDATE daily_stats SET {action_type} = {action_type} + 1 WHERE date = ?',
                (today,)
            )
        else:
            cursor.execute(
                'INSERT INTO daily_stats (date, follows, likes, comments, unfollows) VALUES (?, 0, 0, 0, 0)',
                (today,)
            )
            cursor.execute(
                f'UPDATE daily_stats SET {action_type} = {action_type} + 1 WHERE date = ?',
                (today,)
            )
        
        conn.commit()
        conn.close()

    def can_perform_action(self, action_type):
        stats = self.get_today_stats()
        daily_limit = self.config['limits'].get(f'daily_{action_type}', 50)
        
        return stats[action_type] < daily_limit

    def follow_user(self, username):
        if not self.can_perform_action('follows'):
            self.logger.warning("Günlük takip limiti doldu")
            return False
        
        try:
            self.driver.get(f"https://www.instagram.com/{username}/")
            self.random_delay()
            
            follow_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Takip Et')]"))
            )
            
            if follow_btn.text == "Takip Et":
                follow_btn.click()
                self.logger.info(f"{username} takip edildi")
                
                self.log_activity('follow', username, True)
                self.update_daily_stats('follows')
                
                conn = sqlite3.connect('instagram_bot.db')
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT OR REPLACE INTO followed_users (username, followed_at) VALUES (?, ?)',
                    (username, datetime.now())
                )
                conn.commit()
                conn.close()
                
                return True
            else:
                self.logger.info(f"{username} zaten takip ediliyor")
                return False
                
        except Exception as e:
            self.logger.error(f"Takip hatası {username}: {e}")
            self.log_activity('follow', username, False)
            return False

    def like_post(self, post_url):
        if not self.can_perform_action('likes'):
            self.logger.warning("Günlük beğeni limiti doldu")
            return False
        
        try:
            self.driver.get(post_url)
            self.random_delay()
            
            like_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[@aria-label='Beğen']//.."))
            )
            
            like_svg = like_btn.find_element(By.TAG_NAME, 'svg')
            if 'fill="#ed4956"' not in like_svg.get_attribute('innerHTML'):
                like_btn.click()
                self.logger.info("Gönderi beğenildi")
                
                self.log_activity('like', post_url, True)
                self.update_daily_stats('likes')
                return True
            else:
                self.logger.info("Gönderi zaten beğenilmiş")
                return False
                
        except Exception as e:
            self.logger.error(f"Beğeni hatası: {e}")
            self.log_activity('like', post_url, False)
            return False

    def comment_post(self, post_url, comment_text):
        if not self.can_perform_action('comments'):
            self.logger.warning("Günlük yorum limiti doldu")
            return False
        
        try:
            self.driver.get(post_url)
            self.random_delay()
            
            comment_area = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Yorum ekle...']"))
            )
            comment_area.click()
            self.random_delay()
            
            comment_input = self.driver.find_element(By.XPATH, "//textarea[@placeholder='Yorum ekle...']")
            comment_input.send_keys(comment_text)
            self.random_delay()
            
            comment_input.send_keys(Keys.RETURN)
            self.logger.info("Yorum eklendi")
            
            self.log_activity('comment', post_url, True)
            self.update_daily_stats('comments')
            return True
            
        except Exception as e:
            self.logger.error(f"Yorum hatası: {e}")
            self.log_activity('comment', post_url, False)
            return False

    def unfollow_user(self, username):
        try:
            self.driver.get(f"https://www.instagram.com/{username}/")
            self.random_delay()
            
            following_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Takip Ediliyor')]"))
            )
            following_btn.click()
            self.random_delay()
            
            unfollow_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Takibi Bırak')]"))
            )
            unfollow_btn.click()
            self.logger.info(f"{username} takip bırakıldı")
            
            self.log_activity('unfollow', username, True)
            self.update_daily_stats('unfollows')
            
            conn = sqlite3.connect('instagram_bot.db')
            cursor = conn.cursor()
            cursor.execute('DELETE FROM followed_users WHERE username = ?', (username,))
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Takip bırakma hatası {username}: {e}")
            self.log_activity('unfollow', username, False)
            return False

    def auto_unfollow(self, days_old=3):
        try:
            conn = sqlite3.connect('instagram_bot.db')
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            cursor.execute(
                'SELECT username FROM followed_users WHERE followed_at < ?',
                (cutoff_date,)
            )
            users_to_unfollow = cursor.fetchall()
            conn.close()
            
            for user in users_to_unfollow:
                if self.unfollow_user(user[0]):
                    self.logger.info(f"{user[0]} takipten çıkarıldı")
                    time.sleep(self.config['timing']['between_actions'])
                    
        except Exception as e:
            self.logger.error(f"Otomatik takip bırakma hatası: {e}")

    def explore_hashtag(self, hashtag, count=10):
        try:
            self.driver.get(f"https://www.instagram.com/explore/tags/{hashtag}/")
            self.random_delay()
            
            posts = self.driver.find_elements(By.XPATH, "//article//a")[:count]
            
            for post in posts:
                post_url = post.get_attribute('href')
                if post_url:
                    self.like_post(post_url)
                    time.sleep(self.config['timing']['between_actions'])
                    
        except Exception as e:
            self.logger.error(f"Hashtag keşif hatası {hashtag}: {e}")

    def auto_follow_hashtag(self, hashtag, count=5):
        try:
            self.driver.get(f"https://www.instagram.com/explore/tags/{hashtag}/")
            self.random_delay()
            
            posts = self.driver.find_elements(By.XPATH, "//article//a")[:count]
            
            for post in posts:
                post_url = post.get_attribute('href')
                if post_url:
                    self.driver.get(post_url)
                    self.random_delay()
                    
                    username_link = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, "//header//a"))
                    )
                    username = username_link.text
                    
                    if username and self.follow_user(username):
                        self.logger.info(f"{username} takip edildi")
                        time.sleep(self.config['timing']['between_actions'])
                        
        except Exception as e:
            self.logger.error(f"Hashtag takip hatası {hashtag}: {e}")

    def run_automation_cycle(self):
        self.logger.info("Otomasyon döngüsü başlatılıyor...")
        
        # Hashtag keşfi ve beğeni
        for hashtag in self.config['targeting']['hashtags'][:2]:
            self.explore_hashtag(hashtag, count=3)
            time.sleep(self.config['timing']['between_actions'])
        
        # Takip et
        for hashtag in self.config['targeting']['hashtags'][2:4]:
            self.auto_follow_hashtag(hashtag, count=2)
            time.sleep(self.config['timing']['between_actions'])
        
        # Eski takipleri temizle
        self.auto_unfollow(days_old=3)
        
        self.logger.info("Otomasyon döngüsü tamamlandı")

    def safe_shutdown(self):
        if self.driver:
            self.driver.quit()
        self.logger.info("Bot güvenli şekilde kapatıldı")

def main():
    parser = argparse.ArgumentParser(description='Instagram Bot')
    parser.add_argument('--username', required=True, help='Instagram kullanıcı adı')
    parser.add_argument('--password', required=True, help='Instagram şifresi')
    parser.add_argument('--mode', choices=['auto', 'follow', 'like', 'unfollow'], 
                       default='auto', help='Çalışma modu')
    parser.add_argument('--target', help='Hedef kullanıcı veya hashtag')
    
    args = parser.parse_args()
    
    bot = InstagramBot()
    
    try:
        bot.setup_driver()
        
        if bot.login(args.username, args.password):
            if args.mode == 'auto':
                bot.run_automation_cycle()
            elif args.mode == 'follow' and args.target:
                bot.follow_user(args.target)
            elif args.mode == 'like' and args.target:
                bot.like_post(args.target)
            elif args.mode == 'unfollow' and args.target:
                bot.unfollow_user(args.target)
                
        time.sleep(5)
        
    except KeyboardInterrupt:
        bot.logger.info("Bot kullanıcı tarafından durduruldu")
    except Exception as e:
        bot.logger.error(f"Beklenmeyen hata: {e}")
    finally:
        bot.safe_shutdown()

if __name__ == "__main__":
    main()
