import requests
import time
import json
import os

# === CONFIGURATION ===

# API Key
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "AIzaSyBj-atBuxjkUNpecYX78sl5QAtabFMt3Sg")

# List of YouTube channel IDs
CHANNELS = [
    "UCb9eK6mcBZmGPWl1UJ2wemA",  # Channel 1
    "UCme1x5ySvBB8lGYsHpR4b6Q",        # Add more channels here if needed
]

# Mapping of keyword → Discord webhook URL
WEBHOOK_MAP = {
    "GLOVE STATION": "https://discord.com/api/webhooks/1436874656224379033/_Nw5lGbnUD0xR8QmBxg5KrctPgKuIc1DU1fmVHcY-OXYloIbmDtC9LYeLTrje_IfSXim",
    "MK FIRE": "https://discord.com/api/webhooks/1436874897514303769/RD3TwnX2XJtOX-Qb20e6FDOdRhfBL8HPoqDMRF3rXyHQvyiqlE-brFhQJGYJrGBAW6UL",
    "INVETS": "https://discord.com/api/webhooks/1436874770728620174/ONn174GUKD8s4co19R6TVkmLMWW8sPwa0hfGnN2THB060D7nnAaJ3I_xLXHBG2iBqP8Q",
    "SAVE22 TRUCK SERIES": "https://discord.com/api/webhooks/1436873764083339335/-nU5XnnjzqUYZYih-_vjI-RqWrkE9LIZ8R-XpBHbae-t1hp_zVqm6L84hfSDhgZhy6GA",
    "CRUSIN CLASSICS": "https://discord.com/api/webhooks/1436874235296481310/khkApEcAstt_dpjlNMH2RzP_-TZMCQOEXfi-mEkZ7UiC4EJbW9ynvmMjvzXPWkqWN_xE",
    "LINCOLN TECH": "https://discord.com/api/webhooks/1436874472908001350/6OOWvxqeXLVAPwpODvvzgvtZjjJ0WVQpb1J-svt0aiyEHa7o56ehu93jRbd481IaVjLf",

    # ✅ New keyword added
    "GOAT TALK LIVE": "https://discord.com/api/webhooks/1437062385985650779/ORBmPYtKNvrwEa410L0LgF9QoE_gT-XoOJQ-kTuaEd4qxOefsofe1RfvqMCaj4Rpnupi"
}

# Separate file for each channel
POSTED_FILE_TEMPLATE = "posted_videos_{}.json"


# === HELPER FUNCTIONS ===

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
    """Fetch the latest videos from the YouTube channel."""
    url = (
        f"https://www.googleapis.com/youtube/v3/search"
        f"?key={YOUTUBE_API_KEY}"
        f"&channelId={channel_id}"
        f"&part=snippet,id"
        f"&order=date"
        f"&maxResults={max_results}"
    )
    response = requests.get(url)
    data = response.json()

    if "items" not in data:
        print(f"⚠️ API error or no videos found for channel: {channel_id}")
        return []

    videos = []
    for item in data["items"]:
        if item["id"].get("videoId"):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            link = f"https://www.youtube.com/watch?v={video_id}"
            thumbnail = item["snippet"]["thumbnails"]["high"]["url"]
            videos.append({
                "id": video_id,
                "title": title,
                "link": link,
                "thumbnail": thumbnail
            })
    return videos


def get_first_matching_keyword(title):
    """Return the first keyword found in the title, or None if no match."""
    title_upper = title.upper()
    for keyword in WEBHOOK_MAP:
        if keyword in title_upper:
            return keyword
    return None


def post_to_discord(webhook_url, video, keyword):
    """Send an embedded message to a Discord webhook."""
    embed = {
        "title": video["title"],
        "url": video["link"],
        "color": 0x1E90FF,
        "image": {"url": video["thumbnail"]},
    }

    payload = {
        "username": "VSPEED :clapper: Broadcast Link",
        "embeds": [embed]
    }

    response = requests.post(webhook_url, json=payload)
    if response.status_code == 204:
        print(f"✅ Posted '{video['title']}' ({keyword})")
    else:
        print(f"⚠️ Failed to post '{video['title']}' ({keyword}) - Status {response.status_code}")


# === MAIN LOOP ===

def main():
    print("🚀 YouTube → Discord integration started (multi-channel mode)...")

    while True:
        for channel_id in CHANNELS:

            print(f"\n🔍 Checking channel: {channel_id}")
            posted_videos = load_posted_videos(channel_id)

            videos = get_latest_videos(channel_id)

            for video in videos:
                if video["id"] in posted_videos:
                    continue

                keyword = get_first_matching_keyword(video["title"])
                if keyword:
                    post_to_discord(WEBHOOK_MAP[keyword], video, keyword)
                    posted_videos.add(video["id"])
                    save_posted_videos(channel_id, posted_videos)

        # ✅ Sleep after checking ALL channels once
        time.sleep(600)  # check every 10 minutes


if __name__ == "__main__":
    main()
