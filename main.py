import os
import requests
import random

# GitHub Secrets থেকে ডাটা নেবে
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

categories = [
    "মহাবিশ্ব, সৃষ্টিতত্ত্ব এবং জ্যোতির্বিজ্ঞান",
    "কোরআনে বর্ণিত নবী-রাসূলদের ঐতিহাসিক ঘটনা ও শিক্ষা",
    "মানব সৃষ্টি, ভ্রূণতত্ত্ব এবং জীববিজ্ঞান",
    "প্রাচীন ধ্বংসপ্রাপ্ত জাতিসমূহ এবং তাদের প্রত্নতাত্ত্বিক প্রমাণ",
    "প্রকৃতি, পর্বত এবং সমুদ্রবিজ্ঞান",
    "কোরআনের নির্দিষ্ট আয়াতের শানে নুযুল এবং ঐতিহাসিক প্রেক্ষাপট",
    "হাদিসের আলোকে স্বাস্থ্যবিজ্ঞান ও চিকিৎসাবিজ্ঞান",
    "রাসূল (সাঃ) ও সাহাবীদের জীবনের শিক্ষণীয় ঘটনা"
]

def generate_and_post():
    category = random.choice(categories)
    seed = random.randint(1, 999999) 
    
    print(f"📁 আজকের ক্যাটাগরি: {category}")
    
    prompt = f"""
    তুমি একজন বিজ্ঞ ইসলামিক স্কলার। আমি তোমাকে একটি ক্যাটাগরি দিচ্ছি: '{category}'। 
    এই বিষয়ের ওপর ভিত্তি করে সম্পূর্ণ নতুন ও শিক্ষণীয় একটি নির্দিষ্ট টপিক নির্বাচন করো (Random Seed: {seed}) এবং টেলিগ্রাম চ্যানেলের জন্য বাংলায় একটি চমৎকার পোস্ট লেখো।
    
    সহজ কিছু নিয়ম মেনে চলবে:
    ১. আকার ও গঠন: লেখাটি ৫০০ শব্দের মধ্যে রাখবে। শুরুতে একটি সুন্দর শিরোনাম দেবে। কোনো সাব-হেডিং বা পয়েন্ট দেওয়ার দরকার নেই, ২-৩টি প্যারায় সাবলীলভাবে লিখবে।
    ২. ফরম্যাটিং: লেখায় কোনো মার্কডাউন (যেমন ** বা #) ব্যবহার করবে না। লেখাকে বোল্ড করতে চাইলে <b>লেখা</b> এবং ইটালিক করতে চাইলে <i>লেখা</i> ট্যাগ ব্যবহার করবে। 
    ৩. কোরআন: কোরআনের রেফারেন্স দিলে প্রথমে আরবি আয়াতটি (হরকতসহ) লিখবে, এরপর একটুস্পেস দিয়ে নতুন লাইনে আয়াতের বাংলা অর্থটি <i>অর্থ...</i> এভাবে ইটালিক করে লিখবে।
    ৪. তাফসির: আয়াতের ব্যাখ্যার জন্য 'তাফসিরে ইবনে কাসীর' বা নির্ভরযোগ্য তাফসিরের রেফারেন্স উল্লেখ করবে।
    ৫. হাদিস: হাদিস ব্যবহার করলে আরবি দেওয়ার দরকার নেই, শুধু বাংলা অর্থটি <i>হাদিসের অর্থ...</i> এভাবে ইটালিক করে লিখবে।
    ৬. বিষয়বস্তু: বিজ্ঞান সম্পর্কিত বিষয় হলে আধুনিক বিজ্ঞানের সাথে কোরআনের মিল তুলে ধরবে। আর ইতিহাস বা নবীদের ঘটনা হলে বিজ্ঞানের দরকার নেই, শুধু ঐতিহাসিক প্রেক্ষাপট ও তাফসির নিয়ে লিখবে।
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        response = requests.post(GEMINI_URL, json=payload)
        data = response.json()
        
        if "candidates" in data:
            raw_text = data['candidates'][0]['content']['parts'][0]['text']
            post_text = raw_text.replace('```html', '').replace('```', '')
            
            tg_payload = {
                "chat_id": CHANNEL_ID,
                "text": post_text,
                "parse_mode": "HTML"
            }
            
            tg_response = requests.post(TELEGRAM_URL, json=tg_payload)
            tg_data = tg_response.json()
            
            if tg_data.get("ok"):
                print("🎉 পোস্ট সফলভাবে পাবলিশ হয়েছে!")
            else:
                print(f"❌ টেলিগ্রাম এরর: {tg_data.get('description')}")
        else:
            print(f"❌ Gemini API Error: {data}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    generate_and_post()
