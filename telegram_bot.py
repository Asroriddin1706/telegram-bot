import os
import yt_dlp
import instaloader
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

# Telegram bot token
TOKEN = "7585111538:AAHRZA6EnGrKxxTIO1eLX2qLprJyikMrRWc"

# YouTube video yuklash
def download_video_youtube(url: str):
    try:
        ydl_opts = {
            'outtmpl': 'downloaded_video.%(ext)s',
            'format': 'bestvideo+bestaudio/best',  # Eng sifatli video va audio
            'quiet': True,  # Kamroq xabarlarni ko'rsatish
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return 'downloaded_video.mp4'
    except Exception as e:
        return f"Xatolik yuz berdi: {str(e)}"

# Instagram video yuklash
def download_video_instagram(url: str):
    try:
        loader = instaloader.Instaloader()
        clean_url = url.split('?')[0]
        shortcode = clean_url.split("/")[-2]
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        if post.is_video:
            video_url = post.video_url
            video_file = 'downloaded_video.mp4'
            response = requests.get(video_url, stream=True)
            with open(video_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return video_file
        else:
            return "Ushbu Instagram post video emas."
    except Exception as e:
        return f"Xatolik yuz berdi: {str(e)}"

# Video yuklashga yordam beruvchi funksiya
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text.strip()
    print(f"Received URL: {url}")

    # "Yuklanmoqda..." yozuvini yuborish
    loading_message = await update.message.reply_text("Yuklanmoqda...")

    if "youtube.com" in url or "youtu.be" in url:
        video_file = download_video_youtube(url)
    elif "instagram.com" in url:
        video_file = download_video_instagram(url)
    else:
        await update.message.reply_text("Faqat YouTube va Instagram linklarini qo'llab-quvvatlayman.")
        await loading_message.delete()
        return

    # Xatolikni tekshirish
    if "Xatolik" in video_file or not os.path.exists(video_file):
        await update.message.reply_text(video_file)
        await loading_message.delete()
        return

    # Video faylni yuborish
    try:
        with open(video_file, 'rb') as f:
            await update.message.reply_video(video=f)
    except Exception as e:
        await update.message.reply_text(f"Video yuborishda xatolik yuz berdi: {str(e)}")

    os.remove(video_file)  # Video faylni o'chirish
    await loading_message.delete()

# Boshlash komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Boshlash", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Assalomu alaykum! Boshlash uchun tugmani bosing.", reply_markup=reply_markup)

# Tugma bosilganda foydalanuvchidan URL so'rash
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'start':
        await query.edit_message_text("Video linkini yuboring (  Instagram):")

# Botni ishga tushirish
def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video))
    application.run_polling()

if __name__ == '__main__':
    main()
