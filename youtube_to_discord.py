import requests
import time
import json
import os

# === CONFIGURATION ===
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "AIzaSyBj-atBuxjkUNpecYX78sl5QAtabFMt3Sg")

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

CHECK_INTERVAL = 600  # 10 minutes

# Track last check timestamp
last_checked = {channel_id: 0 for channel_id in CHANNELS}


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
    response = requests.get(url)
    return response.json().get("items", [])


def get_first_matching_keyword(title):
    title_upper = title.upper()
    for keyword in WEBHOOK_MAP:
        if keyword in title_upper:
            return keyword
    return None


def main():
    print("✅ YouTube → Discord service started with cooldown protection")

    while True:
        now = time.time()

        for channel_id in CHANNELS:
            # Only check a channel if cooldown passed
            if now - last_checked[channel_id] < CHECK_INTERVAL:
                continue

            last_checked[channel_id] = now

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
                    print(f"🎯 Match: {title} → {keyword}")
                    requests.post(webhook, json={
                        "username": "VSPEED 🎬 Broadcast Link",
                        "embeds": [{
                            "title": title,
                            "url": link,
                            "color": 0x1E90FF,
                            "image": {"url": snippet["thumbnails"]["high"]["url"]}
                        }]
                    })
                    posted.add(video_id)
                    save_posted_videos(channel_id, posted)

        time.sleep(2)  # Very small sleep to prevent CPU spinning


if __name__ == "__main__":
    main()
