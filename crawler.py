import os
import time
import random
import requests

# পরিবেশ ভ্যারিয়েবল থেকে তথ্য নেওয়া হবে (সুরক্ষার জন্য)
API_URL = os.environ.get("API_URL", "https://crm.fusionminute.com")
API_KEY = os.environ.get("API_KEY", "")

# সাধারণ ব্রাউজারের পরিচয় সিমুলেট করার জন্য
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0"
]

def run_crawler():
    if not API_KEY:
        print("Error: API_KEY পাওয়া যায়নি!")
        return

    # ১. cPanel ড্যাশবোর্ড থেকে একটিভ লিংকগুলো সংগ্রহ করা
    fetch_url = f"{API_URL.rstrip('/')}/index.php?api=get_targets&key={API_KEY}"
    try:
        response = requests.get(fetch_url, timeout=15)
        response.raise_for_status()
        data = response.json()
        targets = data.get("targets", [])
    except Exception as e:
        print(f"ড্যাশবোর্ড থেকে তথ্য আনা সম্ভব হয়নি: {e}")
        return

    if not targets:
        print("ভিজিট করার মতো কোনো সক্রিয় লিংক নেই।")
        return

    print(f"মোট {len(targets)}টি সক্রিয় লিংক পাওয়া গেছে। কার্যক্রম শুরু হচ্ছে...")

    # ২. প্রতিবার কার্যক্রম শুরুর আগে ২ থেকে ৫ মিনিটের একটি র‍্যান্ডম বিরতি (যাতে ভিজিটের নির্দিষ্ট প্যাটার্ন তৈরি না হয়)
    initial_wait = random.randint(60, 240)
    print(f"স্বাভাবিক ভিজিট নিশ্চিত করতে {initial_wait} সেকেন্ড অপেক্ষা করা হচ্ছে...")
    time.sleep(initial_wait)

    # ৩. প্রতিটি পেজ ভিজিট করা
    for target in targets:
        target_id = target.get("id")
        url = target.get("url")

        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
        }

        start_time = time.time()
        status_code = 0
        try:
            res = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
            status_code = res.status_code
        except Exception as err:
            print(f"ভিজিট ব্যর্থ হয়েছে ({url}): {err}")
            status_code = 500

        duration_ms = int((time.time() - start_time) * 1000)
        print(f"ভিজিট সম্পন্ন: {target.get('title')} | কোড: {status_code} | সময়: {duration_ms}ms")

        # ৪. cPanel ড্যাশবোর্ডে ফলাফল পাঠানো
        update_url = f"{API_URL.rstrip('/')}/index.php?api=update_status&key={API_KEY}"
        payload = {
            "id": target_id,
            "status_code": status_code,
            "duration_ms": duration_ms
        }
        try:
            requests.post(update_url, json=payload, timeout=10)
        except Exception as err:
            print(f"ড্যাশবোর্ডে স্ট্যাটাস আপডেট পাঠানো যায়নি: {err}")

        # দুই পেজ ভিজিটের মাঝে ৩–১০ সেকেন্ডের ছোট বিরতি
        time.sleep(random.randint(3, 10))

    print("সকল পেজ সফলভাবে ভিজিট করা হয়েছে।")

if __name__ == "__main__":
    run_crawler()
