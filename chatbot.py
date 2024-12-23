from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Функция для команды /start
async def start(update: Update, context: CallbackContext) -> None:
    # Создаём кнопки
    keyboard = [
        ["Ну привет, Таприскен"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Привет, ПАОВ!",
        reply_markup=reply_markup
    )

# Функция для обработки текстов
async def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text

    if text == "Ну привет, Таприскен":
        await update.message.reply_text("Кек")
    else:
        await update.message.reply_text("Я не знаю, как на это ответить.")

def main():
    # Вставьте ваш токен
    token = "7614855946:AAGsujjZe8Vb36mVrDujapTUjDWx-jZnLIA"
    application = Application.builder().token(token).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    print("Бот запущен. Нажмите Ctrl+C для остановки.")
    application.run_polling()

if __name__ == "__main__":
    main()
