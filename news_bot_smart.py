import feedparser
import time
import requests
import os
from bs4 import BeautifulSoup

# কনফিগারেশন (GitHub Secrets থেকে তথ্য নিবে)
API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CH_ID = "@news24bdlive" 
RSS_URL = "https://www.prothomalo.com/feed"

seen_links = set()

def send_to_telegram(summary, img_url):
    tele_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    payload = {"chat_id": CH_ID, "photo": img_url, "caption": summary, "parse_mode": "HTML"}
    try:
        r = requests.post(tele_url, data=payload)
        if r.status_code == 200:
            print("✅ গুরুত্বপূর্ণ নিউজ চ্যানেলে পোস্ট করা হয়েছে।")
    except:
        pass

def get_ai_summary(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.content, 'html.parser')
        img = soup.find('meta', property='og:image')['content'] if soup.find('meta', property='og:image') else ""
        paras = " ".join([p.get_text().strip() for p in soup.find_all('p') if len(p.get_text().strip()) > 40])
        
        if not paras or not img: return

        list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
        list_res = requests.get(list_url).json()
        available_model = next((m['name'] for m in list_res.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', []) and ('flash' in m['name'].lower() or 'pro' in m['name'].lower())), "")

        if not available_model: return

        api_url = f"https://generativelanguage.googleapis.com/v1beta/{available_model}:generateContent?key={API_KEY}"
        
        prompt = f"""
        নিচের খবরটি পড়ো। 
        ১. যদি খবরটি অত্যন্ত গুরুত্বপূর্ণ বা পাবলিক ইন্টারেস্টের হয়, তবে ৩-৪ লাইনের একটি প্রফেশনাল সারসংক্ষেপ তৈরি করো।
        ২. যদি খবরটি সাধারণ বা অগুরুত্বপূর্ণ হয়, তবে শুধু 'IGNORE' শব্দটি লেখো।
        ৩. সারসংক্ষেপে কোনো ইমোজি, শিরোনাম বা লিঙ্ক ব্যবহার করবে না।
        ৪. সম্পূর্ণ সারসংক্ষেপ একটি প্যারায় হতে হবে।
        
        খবর: {paras}
        """
        
        ai_res = requests.post(api_url, json={"contents": [{"parts": [{"text": prompt}]}]}, headers={'Content-Type': 'application/json'})
        
        if ai_res.status_code == 200:
            result = ai_res.json()['candidates'][0]['content']['parts'][0]['text'].strip()
            if "IGNORE" not in result.upper():
                summary = " ".join(result.split())
                send_to_telegram(summary, img)
            else:
                print("⏭️ খবরটি গুরুত্বপূর্ণ নয় বলে বাদ দেওয়া হয়েছে।")
                
    except Exception as e:
        print(f"❌ প্রসেসিং এরর: {e}")

print("🚀 স্মার্ট নিউজ বট চালু হয়েছে...")
initial_feed = feedparser.parse(RSS_URL)
for entry in initial_feed.entries:
    seen_links.add(entry.link)

# ৩৪০ মিনিট (৫ ঘণ্টা ৪০ মিনিট) পর্যন্ত লুপ চলবে, তারপর গিটহাব রিস্টার্ট দিবে
start_time = time.time()
while (time.time() - start_time) < (340 * 60):
    try:
        feed = feedparser.parse(RSS_URL)
        for entry in feed.entries:
            if entry.link not in seen_links:
                print(f"📰 নতুন খবর পাওয়া গেছে: {entry.title}")
                get_ai_summary(entry.link)
                seen_links.add(entry.link)
        time.sleep(30)
    except:
        time.sleep(10)
