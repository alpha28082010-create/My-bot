import os
import requests
import telebot

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(
        message,
        "Assalomu alaykum! Menga YouTube (Shorts), Instagram yoki TikTok havolasini yuboring, men uni sizga yuklab beraman.",
    )


def get_download_link(url):
    """1-Manba: Cobalt API"""
    try:
        api_url = "https://api.cobalt.tools/api/json"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
        }
        payload = {"url": url, "vQuality": "720"}
        res = requests.post(
            api_url, json=payload, headers=headers, timeout=10
        ).json()

        if "url" in res:
            return res["url"]
        elif "picker" in res and len(res["picker"]) > 0:
            return res["picker"][0]["url"]
    except Exception as e:
        print(f"Cobalt error: {e}")

    """ 2-Zaxira Manba: SSYouTube / SaveFrom API """
    try:
        api_url = "https://worker.sf-helper.com/project/sf-helper/api/download"
        res = requests.post(api_url, data={"url": url}, timeout=10).json()
        if "url" in res and len(res["url"]) > 0:
            return res["url"][0]["url"]
    except Exception as e:
        print(f"SaveFrom error: {e}")

    return None


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()

    if not (url.startswith("http://") or url.startswith("https://")):
        bot.reply_to(message, "Iltimos, to'g'ri video havolasini yuboring!")
        return

    msg = bot.reply_to(message, "⏳ Video tayyorlanmoqda, kuting...")

    try:
        video_url = get_download_link(url)

        if not video_url:
            bot.edit_message_text(
                "❌ Videoni yuklab bo'lmadi. Havolani tekshiring yoki keyinroq urinib ko'ring.",
                message.chat.id,
                msg.message_id,
            )
            return

        bot.edit_message_text(
            "🚀 Video yuklanmoqda...", message.chat.id, msg.message_id
        )

        # Videoni URL'dan fayl sifatida yuklab olib yuborish (Telegram havola orqali xato berishini oldini oladi)
        video_bytes = requests.get(video_url, stream=True, timeout=30)

        with open("video.mp4", "wb") as f:
            for chunk in video_bytes.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

        with open("video.mp4", "rb") as video_file:
            bot.send_video(
                message.chat.id,
                video_file,
                caption="🤖 @SaveMedia_bot orqali yuklandi",
            )

        # Vaqtinchalik faylni o'chirish
        if os.path.exists("video.mp4"):
            os.remove("video.mp4")

        bot.delete_message(message.chat.id, msg.message_id)

    except Exception as e:
        bot.edit_message_text(
            f"❌ Xatolik yuz berdi: {str(e)}", message.chat.id, msg.message_id
        )
        if os.path.exists("video.mp4"):
            os.remove("video.mp4")


if __name__ == "__main__":
    print("Bot ishga tushdi...")
    bot.infinity_polling()
