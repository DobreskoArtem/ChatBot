from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import os
from threading import Thread

app = Flask(__name__)

# Получаем токен бота и OWNER_CHAT_ID из переменных окружения
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Токен бота
OWNER_CHAT_ID = os.getenv("OWNER_CHAT_ID")  # ID владельца бота

# Проверяем, заданы ли переменные окружения
if TOKEN is None:
    raise ValueError("Переменная окружения TELEGRAM_BOT_TOKEN не задана.")
if OWNER_CHAT_ID is None:
    raise ValueError("Переменная окружения OWNER_CHAT_ID не задана.")

OWNER_CHAT_ID = int(OWNER_CHAT_ID)  # Преобразуем в число

# Инициализация приложения Telegram Bot
application = Application.builder().token(TOKEN).build()


# Обработчики команд и сообщений
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Опишите вашу проблему, и я передам её владельцу бота.')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_chat_id = update.message.chat_id
    user_message = update.message.text
    await context.bot.send_message(chat_id=OWNER_CHAT_ID,
                                   text=f"Сообщение от пользователя {user_chat_id}:\n{user_message}")
    await update.message.reply_text('Ваше сообщение отправлено владельцу бота. Ожидайте ответа.')


async def handle_owner_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.reply_to_message:
        original_message = update.message.reply_to_message.text
        user_chat_id = int(original_message.split()[3])
        await context.bot.send_message(chat_id=user_chat_id, text=f"Ответ от владельца бота:\n{update.message.text}")


# Регистрация обработчиков
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
application.add_handler(MessageHandler(filters.REPLY, handle_owner_reply))


@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put(update)
    return 'ok'


def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    # Установка вебхука
    application.bot.set_webhook(url="https://your-bot-name.onrender.com/webhook")

    # Запуск Flask в отдельном потоке
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Запуск Telegram Bot
    application.run_polling()