import os, time, threading, requests
from datetime import datetime
from telegram import Bot, Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
INTERVAL_HOURS = int(os.getenv("CHECK_INTERVAL_HOURS", 6))
URL = "https://minha.anem.dz/pre_rendez_vous"

bot = Bot(token=BOT_TOKEN)
last_status = "غير معروف"
last_checked = None

def check_site():
    global last_status, last_checked
    try:
        r = requests.get(URL, timeout=15)
        text = r.text
        last_checked = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if "لا يوجد أي موعد متاح حاليا" in text:
            new_status = "🚫 لا يوجد مواعيد حالياً."
        else:
            new_status = "✅ تم فتح موعد جديد!"

        if new_status != last_status:
            bot.send_message(chat_id=CHAT_ID, text=new_status)
            last_status = new_status

    except Exception as e:
        bot.send_message(chat_id=CHAT_ID, text=f"⚠️ حدث خطأ: {e}")

def periodic_check():
    while True:
        check_site()
        time.sleep(INTERVAL_HOURS * 3600)

def manual_check(update: Update, context: CallbackContext):
    check_site()
    update.message.reply_text(f"تم الفحص الآن:\n{last_status}\nآخر تحقق: {last_checked}")

def get_status(update: Update, context: CallbackContext):
    update.message.reply_text(f"آخر حالة: {last_status}\nآخر فحص: {last_checked}")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.regex("^(تحقق|check)$"), manual_check))
    dp.add_handler(MessageHandler(Filters.regex("^(الحالة|status)$"), get_status))
    threading.Thread(target=periodic_check, daemon=True).start()
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
