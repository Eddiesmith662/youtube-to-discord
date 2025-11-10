import requests
import time
import json
import os

# === CONFIGURATION ===
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if not YOUTUBE_API_KEY:
    raise ValueError("Missing YOUTUBE_API_KEY environment variable!")


CHANNELS = [
    "UCb9eK6mcBZmGPWl1UJ2wemA",
    "UCme1x5ySvBB8lGYsHpR4b6Q",
]

WEBHOOK_MAP = {
    "GLOVE STATION": "https://discord.com/api/webhooks/1436874656224379033/_Nw5lGbnUD0xR8QmBxg5KrctPgKuIc1DU1fmVHcY-OXYloIbmDtC9LYeLTrje_IfSXim",
    "MK FIRE": "https://discord.com/api/webhooks/1436874897514303769/RD3TwnX2XJtOX-Qb20e6FDOdRhfBL8HPoqDMRF3rXyHQvyiqlE-brFhQJGYJrGBAW6UL",
    "INVETS": "https://discord.com/api/webhooks/1436874770728620174/ONn174GUKD8s4co19R6TVkmLMWW8sPwa0hfGnN2THB060D7nnAaJ3I_xLXHBG2iBqP8Q",
    "SAVE22 TRUCK SERIES": "https://discord.com/api/webhooks/1436873764083339335/-nU5XnnjzqUYZYih-_vjI-RqWrkE9LIZ8R-XpBHbae-t1hp_zVqm6L84hfSDhgZhy6GA",
    "CRUSIN CLASSICS": "https://discord.com/api/webhooks/1436874235296481310/khkApEcAstt_dpjlNMH2RzP_-TZMCQOEXfi-mEkZ7UiC4EJbW9ynvmMjvzXPWkqWN_xE",
    "LINCOLN TECH": "https://discord.com/api/webhooks/1436874472908001350/6OOWvxqeXLVAPwpODvvzgvtZjjJ0WVQpb1J-svt0aiyEHa7o56ehu93jRbd481IaVjLf",
    "GOAT TALK LIVE": "https://discord.com/api/webhooks/1437062385985650779/ORBmPYtKNvrwEa410L0LgF9QoE_gT-XoOJQ-kTuaEd4qxOefsofe1RfvqMCaj4Rpnupi"
}

POSTED_FILE_TEMPLATE = "posted_videos_{}.json"
CHECK_INTERVAL = 3600   # 1 hour


def load_posted_videos(channel_id):
    filename = POSTED_FILE_TEMPLATE.format(channel_id)
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return set(json.load(f))
    return set()


def save_posted_videos(channel_id, posted):
    filename = POSTED_FILE_TEMPLATE.format(channel_id)
    with open(filename, "w") as f:
        json.dump(list(posted), f)


def get_latest_videos(channel_id, max_results=5):
    url = (
        f"https://www.googleapis.com/youtube/v3/search"
        f"?key={YOUTUBE_API_KEY}"
        f"&channelId={channel_id}"
        f"&part=snippet,id"
        f"&order=date"
        f"&maxResults={max_results}"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json().get("items", [])
    except Exception as e:
        print(f"⚠️ Error fetching videos for {channel_id}: {e}")
        return []


def get_first_matching_keyword(title):
    title_upper = title.upper()
    for keyword in WEBHOOK_MAP:
        if keyword in title_upper:
            return keyword
    return None


def main():
    print("✅ YouTube → Discord service started (hourly check mode)")

    while True:
        for channel_id in CHANNELS:
            print(f"\n⏳ Checking channel: {channel_id}")
            posted = load_posted_videos(channel_id)

            items = get_latest_videos(channel_id)
            for item in items:
                video_id = item["id"].get("videoId")
                if not video_id or video_id in posted:
                    continue

                snippet = item["snippet"]
                title = snippet["title"]
                keyword = get_first_matching_keyword(title)

                if keyword:
                    link = f"https://www.youtube.com/watch?v={video_id}"
                    webhook = WEBHOOK_MAP[keyword]
                    thumb = snippet["thumbnails"]["high"]["url"]

                    print(f"🎯 Match: {title} → {keyword}")

                    requests.post(webhook, json={
                        "username": "VSPEED 🎬 Broadcast Link",
                        "embeds": [{
                            "title": title,
                            "url": link,
                            "color": 0x1E90FF,
                            "image": {"url": thumb}
                        }]
                    })

                    posted.add(video_id)
                    save_posted_videos(channel_id, posted)

        print(f"😴 Sleeping for {CHECK_INTERVAL} seconds...")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
