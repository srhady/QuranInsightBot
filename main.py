import os
import requests
import random

# GitHub Secrets থেকে ডাটা নেবে
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
HISTORY_FILE = "history.txt"
POST_NUMBER_FILE = "post_number.txt" # নতুন ট্র্যাকার

# বিশাল এবং বৈচিত্র্যময় ক্যাটাগরি লিস্ট (মোট ২৩টি)
categories = [
    "মহাবিশ্ব, সৃষ্টিতত্ত্ব এবং জ্যোতির্বিজ্ঞান",
    "কোরআনে বর্ণিত নবী-রাসূলদের ঐতিহাসিক ঘটনা ও শিক্ষা",
    "মানব সৃষ্টি, ভ্রূণতত্ত্ব এবং জীববিজ্ঞান",
    "প্রাচীন ধ্বংসপ্রাপ্ত জাতিসমূহ এবং তাদের প্রত্নতাত্ত্বিক প্রমাণ",
    "প্রকৃতি, পর্বত এবং সমুদ্রবিজ্ঞান",
    "কোরআনের নির্দিষ্ট আয়াতের শানে নুযুল এবং ঐতিহাসিক প্রেক্ষাপট",
    "হাদিসের আলোকে স্বাস্থ্যবিজ্ঞান ও চিকিৎসাবিজ্ঞান",
    "রাসূল (সাঃ) ও সাহাবীদের জীবনের শিক্ষণীয় ঘটনা",
    "কিয়ামত, পরকাল এবং জান্নাত-জাহান্নামের বর্ণনা",
    "ফেরেশতা এবং জ্বীন জাতির রহস্য ও কোরআনের ব্যাখ্যা",
    "ইসলামী আখলাক, উত্তম চরিত্র এবং মানবিক মূল্যবোধ",
    "কোরআনে বর্ণিত নারী চরিত্র এবং তাদের শিক্ষণীয় অবদান",
    "দৈনন্দিন জীবনে রাসূল (সাঃ) এর সুন্নাহ এবং এর বৈজ্ঞানিক উপকারিতা",
    "ইবাদতের (নামাজ, রোজা, জাকাত, হজ) দার্শনিক ও বৈজ্ঞানিক তাৎপর্য",
    "কোরআন ও হাদিসের আলোকে মানসিক শান্তি ও সাইকোলজি",
    "কোরআনে উল্লিখিত বিভিন্ন প্রাণী ও তাদের সৃষ্টিগত বিস্ময়",
    "ইসলামী অর্থনীতি, জাকাত এবং হালাল উপার্জনের বরকত",
    "নবী-রাসূলদের মোজেজা (অলৌকিক ঘটনা) এবং তার যৌক্তিক বিশ্লেষণ",
    "বিপদ-আপদে সবর (ধৈর্য) এবং শুকরিয়া (কৃতজ্ঞতা) আদায়ের কোরআনিক নির্দেশনা",
    "কোরআনের গুরুত্বপূর্ণ দোয়া, শানে নুযুল এবং কবুল হওয়ার শর্ত",
    "ইসলামের সোনালী যুগ এবং মুসলিম বিজ্ঞানীদের আবিষ্কার",
    "সামাজিক ন্যায়বিচার, মানবাধিকার এবং প্রতিবেশীর হক",
    "ইসলামের ঐতিহাসিক যুদ্ধসমূহ (বদর, ওহুদ, খন্দক) এবং এর কৌশলগত শিক্ষা"
]

# মেমোরি থেকে সবগুলো টপিক পড়ার ফাংশন
def read_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return f.read().splitlines()
    return []

# নতুন টপিক মেমোরিতে সেভ করার ফাংশন
def save_history(title):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(title + "\n")

# 📌 পোস্ট নাম্বার ম্যানেজ করার নতুন ফাংশন
def get_and_update_post_number():
    if os.path.exists(POST_NUMBER_FILE):
        with open(POST_NUMBER_FILE, "r", encoding="utf-8") as f:
            num = int(f.read().strip())
    else:
        num = 19 # প্রথমবার ১৯ থেকে শুরু হবে
        
    # পরের বারের জন্য নাম্বার ১ বাড়িয়ে সেভ করে রাখা
    with open(POST_NUMBER_FILE, "w", encoding="utf-8") as f:
        f.write(str(num + 1))
        
    return num

def generate_and_post():
    category = random.choice(categories)
    seed = random.randint(100000, 999999) 
    past_topics = read_history()
    
    # হিস্ট্রি ফাইলের হিসেব বাদ দিয়ে সরাসরি ট্র্যাকার থেকে নাম্বার নিচ্ছে
    post_number = get_and_update_post_number()
    
    # এআই-কে আগের টপিকগুলোর কথা মনে করিয়ে দেওয়া
    history_text = ", ".join(past_topics) if past_topics else "এখনো কোনো পোস্ট করা হয়নি।"
    
    print(f"📁 আজকের ক্যাটাগরি: {category}")
    print(f"🔢 পোস্ট নাম্বার: {post_number}")
    
    prompt = f"""
    তুমি একজন বিজ্ঞ ইসলামিক স্কলার। আমি তোমাকে একটি ক্যাটাগরি দিচ্ছি: '{category}'। 
    
    🚨 অত্যন্ত জরুরি নির্দেশ: 
    তুমি অতীতে নিচের টপিকগুলোর উপর ইতিমধ্যে পোস্ট লিখেছো:
    [{history_text}]
    তোমার কাজ হলো, এই টপিকগুলো সম্পূর্ণ বাদ দিয়ে (Random Seed: {seed} ব্যবহার করে) এই ক্যাটাগরির ভেতর থেকে একদম নতুন, আনকমন এবং বিরল একটি বিষয় খুঁজে বের করা, যা আগে কখনো আলোচনা হয়নি।
    
    সহজ কিছু নিয়ম মেনে চলবে:
    ১. আকার ও গঠন: লেখাটি ৪০০ শব্দের মধ্যে রাখবে। শুরুতে একটি সুন্দর শিরোনাম <b>বোল্ড</b> করে দেবে। কোনো সাব-হেডিং বা পয়েন্ট দেওয়ার দরকার নেই, ২-৩টি প্যারায় সাবলীলভাবে লিখবে। 
    ২. ফরম্যাটিং: লেখায় কোনো মার্কডাউন (যেমন ** বা #) ব্যবহার করবে না। লেখাকে বোল্ড করতে চাইলে <b>লেখা</b> এবং ইটালিক করতে চাইলে <i>লেখা</i> ট্যাগ ব্যবহার করবে। 
    ৩. কোরআন: কোরআনের রেফারেন্স দিলে প্রথমে আরবি আয়াতটি (হরকতসহ) লিখবে। এরপর একটি ফাঁকা লাইন রেখে আয়াতের বাংলা অর্থটি <blockquote><i>অর্থ...</i></blockquote> এই ট্যাগে লিখবে। অর্থের নিচেই অবশ্যই <b>(সূরা: নাম, আয়াত: নম্বর)</b> উল্লেখ করবে।
    ৪. তাফসির: আয়াতের ব্যাখ্যার জন্য 'তাফসিরে ইবনে কাসীর' বা নির্ভরযোগ্য তাফসিরের রেফারেন্স উল্লেখ করবে।
    ৫. হাদিস: হাদিস ব্যবহার করলে শুধুমাত্র <blockquote><i>হাদিসের অর্থ...</i></blockquote> এই ট্যাগের ভেতরে লিখবে। নিচেই অবশ্যই <b>(সূত্র: হাদিস গ্রন্থের নাম ও নম্বর)</b> উল্লেখ করবে।
    ৬. বিষয়বস্তু: বিজ্ঞান সম্পর্কিত বিষয় হলে আধুনিক বিজ্ঞানের সাথে কোরআনের মিল তুলে ধরবে। আর ইতিহাস বা নবীদের ঘটনা হলে বিজ্ঞানের দরকার নেই, শুধু ঐতিহাসিক প্রেক্ষাপট ও তাফসির নিয়ে লিখবে।
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        response = requests.post(GEMINI_URL, json=payload)
        data = response.json()
        
        if "candidates" in data:
            raw_text = data['candidates'][0]['content']['parts'][0]['text']
            
            # ক্লিনআপ: AI ভুল করে <br> ট্যাগ দিলেও তা সাধারণ নিউ লাইনে রূপান্তর হবে
            post_text = raw_text.replace('```html', '').replace('```', '').replace('<br>', '\n').replace('<br/>', '\n')
            
            # 📌 এখানে পোস্টের একদম শুরুতে পোস্ট নাম্বার যুক্ত করা হচ্ছে
            final_post_text = f"<b>পোস্ট নং: {post_number}</b>\n\n{post_text}"
            
            tg_payload = {
                "chat_id": CHANNEL_ID,
                "text": final_post_text,
                "parse_mode": "HTML"
            }
            
            tg_response = requests.post(TELEGRAM_URL, json=tg_payload)
            tg_data = tg_response.json()
            
            if tg_data.get("ok"):
                print(f"🎉 পোস্ট নং {post_number} সফলভাবে পাবলিশ হয়েছে!")
                
                # পোস্টের প্রথম লাইনটি (শিরোনাম) মেমোরিতে সেভ করে রাখা
                title = post_text.strip().split('\n')[0].replace('<b>', '').replace('</b>', '').strip()
                save_history(title[:100]) # প্রথম ১০০ অক্ষর সেভ হবে
                print(f"💾 টপিকটি মেমোরিতে সেভ করা হয়েছে: {title}")
                
            else:
                print(f"❌ টেলিগ্রাম এরর: {tg_data.get('description')}")
        else:
            print(f"❌ Gemini API Error: {data}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    generate_and_post()
