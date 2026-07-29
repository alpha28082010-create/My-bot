import os
import re
import requests
import telebot

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)


def clean_youtube_url(url):
    """Havoladagi ortiqcha va xato beruvchi belgilarni o'chirish"""
    match = re.search(r"(shorts/|v=)([a-zA-Z0-9_-]{11})", url)
    if match:
        video_id = match.group(2)
        return f"https://www.youtube.com/watch?v={video_id}"
    return url


def get_video_download_url(url):
    cleaned_url = clean_youtube_url(url)

    # 1-Manba: Cobalt (To'g'rilangan domen va sozlamalar)
    try:
        cobalt_url = "https://api.cobalt.tools/api/json"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        }
        payload = {
            "url": cleaned_url,
            "vQuality": "720",
            "filenamePattern": "basic",
        }
        res = requests.post(
            cobalt_url, json=payload, headers=headers, timeout=12
        ).json()

        if "url" in res:
            return res["url"]
        elif "picker" in res and len(res["picker"]) > 0:
            return res["picker"][0]["url"]
    except Exception as e:
        print(f"Cobalt xatosi: {e}")

    # 2-Manba: Auto-Downloader API (Aylanma zaxira)
    try:
        api_url = f"https://api.v2.cobalt.tools/api/json"
        res = requests.post(
            api_url, json={"url": cleaned_url}, headers=headers, timeout=10
        ).json()
        if "url" in res:
            return res["url"]
    except Exception as e:
        print(f"Zaxira API xatosi: {e}")

    return None


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(
        message,
        "Assalomu alaykum! YouTube, Instagram yoki TikTok video havolasini yuboring.",
    )


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()

    if not ("youtube.com" in url or "youtu.be" in url or "http" in url):
        bot.reply_to(message, "Iltimos, to'g'ri video havolasini yuboring!")
        return

    msg = bot.reply_to(message, "⏳ Video tayyorlanmoqda, kuting...")

    try:
        download_url = get_video_download_url(url)

        if not download_url:
            bot.edit_message_text(
                "❌ Videoni yuklab bo'lmadi. Server vaqtincha band, birozdan so'ng qayta urinib ko'ring.",
                message.chat.id,
                msg.message_id,
            )
            return

        bot.edit_message_text(
            "🚀 Video yuklanmoqda...", message.chat.id, msg.message_id
        )

        # Videoni oqim (stream) orqali yuborish
        video_res = requests.get(download_url, stream=True, timeout=40)

        with open("video.mp4", "wb") as f:
            for chunk in video_res.iter_content(chunk_size=2048 * 1024):
                if chunk:
                    f.write(chunk)

        with open("video.mp4", "rb") as video_file:
            bot.send_video(
                message.chat.id,
                video_file,
                caption="🤖 @SaveMedia_bot orqali yuklandi",
            )

        bot.delete_message(message.chat.id, msg.message_id)

    except Exception as e:
        bot.edit_message_text(
            f"❌ Xatolik yuz berdi: {str(e)}", message.chat.id, msg.message_id
        )
    finally:
        if os.path.exists("video.mp4"):
            os.remove("video.mp4")


if __name__ == "__main__":
    bot.infinity_polling()
