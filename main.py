import os
import requests
import telebot

# Render'dagi Environment Variables'dan BOT_TOKEN'ni olish
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(
        message,
        "Assalomu alaykum! Menga YouTube, Instagram yoki TikTok video havolasini yuboring, men uni sizga yuklab beraman.",
    )


def get_media_url(url):
    """Cobalt API orqali video yuklash havolasini olish"""
    api_url = "https://api.cobalt.tools/api/json"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {"url": url, "vQuality": "720"}

    response = requests.post(api_url, json=payload, headers=headers, timeout=15)
    data = response.json()

    # Agar API video havolasini qaytarsa
    if "url" in data:
        return data["url"]
    elif "picker" in data and len(data["picker"]) > 0:
        return data["picker"][0]["url"]
    else:
        return None


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()

    # Havolani tekshirish
    if not url.startswith("http://") and not url.startswith("https://"):
        bot.reply_to(message, "Iltimos, to'g'ri video havolasini yuboring!")
        return

    msg = bot.reply_to(message, "⏳ Video tayyorlanmoqda, kuting...")

    try:
        video_url = get_media_url(url)

        if video_url:
            bot.edit_message_text(
                "🚀 Video yuklanmoqda...", message.chat.id, msg.message_id
            )
            # Videoni Telegram'ga yuborish
            bot.send_video(message.chat.id, video_url, caption=" @SaveMedia_bot")
            bot.delete_message(message.chat.id, msg.message_id)
        else:
            bot.edit_message_text(
                "❌ Videoni yuklab bo'lmadi. Havola to'g'riligini tekshiring.",
                message.chat.id,
                msg.message_id,
            )

    except Exception as e:
        bot.edit_message_text(
            f"❌ Xatolik yuz berdi: {str(e)}", message.chat.id, msg.message_id
        )


if __name__ == "__main__":
    print("Bot ishga tushdi...")
    bot.infinity_polling()
