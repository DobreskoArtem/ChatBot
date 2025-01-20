from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import pg8000
from datetime import datetime, timedelta
import openpyxl
from io import BytesIO

# Токен бота
TOKEN = "7614855946:AAGsujjZe8Vb36mVrDujapTUjDWx-jZnLIA"

# Параметры подключения к базе данных PostgreSQL
DB_HOST = 'localhost'
DB_PORT = 5432
DB_NAME = 'my_bot_db'
DB_USER = 'postgres'
DB_PASSWORD = 'postgre'

# Функция для проверки, зарегистрирован ли пользователь
def is_registered(user_id):
    try:
        with pg8000.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=DB_NAME) as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
                result = cursor.fetchone()
        return result is not None
    except Exception as e:
        print(f"Ошибка при проверке регистрации: {e}")
        return False

# Функция для регистрации пользователя
def register_user(user_id, username):
    try:
        with pg8000.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=DB_NAME) as conn:
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO users (user_id, username) VALUES (%s, %s)', (user_id, username))
                conn.commit()
    except Exception as e:
        print(f"Ошибка при регистрации пользователя: {e}")

# Функция для удаления пользователя
def unregister_user(user_id):
    try:
        with pg8000.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=DB_NAME) as conn:
            with conn.cursor() as cursor:
                cursor.execute('DELETE FROM users WHERE user_id = %s', (user_id,))
                conn.commit()
    except Exception as e:
        print(f"Ошибка при удалении пользователя: {e}")


# Функция для проверки, занято ли выбранное время
def is_time_slot_taken(date_time):
    try:
        # Убираем лишний текст 'time ' из строки, если он есть
        date_time = date_time.replace('time ', '')  # Убираем "time" из строки

        # Преобразуем строку в формат datetime
        appointment_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M')

        with pg8000.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=DB_NAME) as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM appointments WHERE appointment_time = %s', (appointment_time,))
                result = cursor.fetchone()

        return result is not None
    except Exception as e:
        print(f"Ошибка при проверке времени: {e}")
        return False


# Функция для записи пользователя на занятие
def book_trial(user_id, date_time):
    try:
        # Убираем лишний текст 'time ' из строки, если он есть
        date_time = date_time.replace('time ', '')  # Убираем "time" из строки

        # Преобразуем строку в формат datetime
        appointment_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M')

        with pg8000.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=DB_NAME) as conn:
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO appointments (user_id, appointment_time) VALUES (%s, %s)',
                               (user_id, appointment_time))
                conn.commit()
    except Exception as e:
        print(f"Ошибка при записи на занятие: {e}")

# Генерация кнопок для выбора даты
def generate_calendar_buttons():
    today = datetime.now()
    buttons = []
    for i in range(7):  # Создадим кнопки на неделю вперед
        date = today + timedelta(days=i)
        button_text = date.strftime('%Y-%m-%d')
        buttons.append([InlineKeyboardButton(button_text, callback_data=f'choose_date_{button_text}')])
    return buttons
# Функция для удаления пользователя
def unregister_user(user_id):
    try:
        with pg8000.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=DB_NAME) as conn:
            with conn.cursor() as cursor:
                cursor.execute('DELETE FROM users WHERE user_id = %s', (user_id,))
                conn.commit()
    except Exception as e:
        print(f"Ошибка при удалении пользователя: {e}")
# Функция для удаления записи пользователя на занятие
def delete_book_trial(user_id, date_time):
    try:
        # Убираем лишний текст 'time ' из строки, если он есть
        date_time = date_time.replace('time ', '')  # Убираем "time" из строки

        # Преобразуем строку в формат datetime
        appointment_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M')

        with pg8000.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=DB_NAME) as conn:
            with conn.cursor() as cursor:
                cursor.execute('DELETE FROM appointments WHERE user_id = %s AND appointment_time = %s',
                               (user_id, appointment_time))
                conn.commit()
    except Exception as e:
        print(f"Ошибка при удалении записи на занятие: {e}")

# Функция для получения расписания пользователя
def get_user_schedule(user_id):
    try:
        with pg8000.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=DB_NAME) as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT appointment_time FROM appointments WHERE user_id = %s ORDER BY appointment_time', (user_id,))
                appointments = cursor.fetchall()

        # Преобразование строковых значений в объекты datetime
        schedule = []
        for appointment in appointments:
            appointment_time = appointment[0]
            if isinstance(appointment_time, str):  # Если данные в формате строки
                appointment_time = datetime.strptime(appointment_time, "%Y-%m-%d %H:%M:%S")
            schedule.append(appointment_time)

        return schedule
    except Exception as e:
        print(f"Ошибка при получении расписания: {e}")
        return "В расписании пусто"

# Функция старта бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['Регистрация']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text('Привет! Нажми на кнопку, чтобы зарегистрироваться.', reply_markup=reply_markup)

#  обработчик для удаления записи на занятие.
async def delete_trial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    schedule = get_user_schedule(user_id)

    if not schedule:
        await update.message.reply_text("У вас нет записей для удаления.")
        return

    # Генерация кнопок для удаления записей
    buttons = [
        [InlineKeyboardButton(f"{appointment.strftime('%d.%m.%Y %H:%M')}", callback_data=f'delete_time_{appointment.strftime("%Y-%m-%d %H:%M")}')]
        for appointment in schedule
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text("Выберите запись для удаления:", reply_markup=reply_markup)

# обработчик выбора записи для удаления.
async def delete_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    selected_time = query.data.split('_', 2)[2]  # Извлекаем дату и время

    # Удаляем запись
    delete_book_trial(user_id, selected_time)

    await query.answer(f"Запись на {selected_time} удалена.")
    await query.edit_message_text(f"Вы успешно удалили запись на {selected_time}.")

# Функция регистрации
async def registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    if is_registered(user_id):
        # Кнопки для зарегистрированного пользователя
        keyboard = [['Записаться на занятие', 'Посмотреть расписание'], ['Выгрузить расписание', 'Удалить запись на занятие', 'Выйти']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text('Вы уже зарегистрированы!', reply_markup=reply_markup)
    else:
        register_user(user_id, username)
        keyboard = [['Записаться на занятие', 'Посмотреть расписание'], ['Выгрузить расписание','Удалить запись на занятие','Выйти']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text('Вы успешно зарегистрированы!', reply_markup=reply_markup)

# Обработчик кнопки "Записаться на пробное занятие"
async def schedule_trial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = generate_calendar_buttons()
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите дату для занятия:', reply_markup=reply_markup)


# Обработчик выбора даты
async def choose_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    selected_date = query.data.split('_')[2]  # Извлекаем выбранную дату

    # Генерация кнопок для выбора времени на выбранную дату
    available_times = ['10:00', '14:00', '16:00']  # Пример доступных времен
    buttons = [
        [InlineKeyboardButton(f'{time} - {selected_date}', callback_data=f'choose_time_{selected_date} {time}')]
        for time in available_times
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    await query.answer()
    await query.edit_message_text('Выберите время для занятия:', reply_markup=reply_markup)

# Обработчик выбора времени
async def choose_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    selected_time = query.data.split('_')[2]  # Время

    # Получаем дату и время для записи
    selected_date = query.data.split('_')[1]  # Дата
    appointment_time = f"{selected_date} {selected_time}"

    # Проверяем, занято ли выбранное время
    if is_time_slot_taken(appointment_time):
        await query.answer('Это время уже занято. Пожалуйста, выберите другое.')
    else:
        # Записываем пользователя
        book_trial(user_id, appointment_time)
        await query.answer(f'Вы записались на занятие на {appointment_time}.')

    # Завершаем обработку
    await query.edit_message_text(f'Вы выбрали {appointment_time}. Спасибо за запись!')

# Обработчик кнопки "Посмотреть расписание"
async def view_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Ваше расписание: Понедельник - 14:00, Среда - 16:00. Напишите администратору для изменения.')

# Обработчик кнопки "Выйти"
async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Отображение кнопок для удаления или выхода без удаления
    keyboard = [
        [InlineKeyboardButton("Удалить все записи", callback_data="delete_all_records")],
        [InlineKeyboardButton("Выйти без удаления", callback_data="logout_without_delete")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

# Функция удаления всех записей
def delete_records(user_id):
    try:
        # Удаление всех записей пользователя
        with pg8000.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=DB_NAME) as conn:
            with conn.cursor() as cursor:
                cursor.execute('DELETE FROM appointments WHERE user_id = %s', (user_id,))
                conn.commit()
    except Exception as e:
        print(f"Ошибка при удалении всех записей: {e}")

# Обработчик кнопки "Удалить все записи"
async def delete_all_records(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    keyboard = [['Регистрация']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text('Вы успешно вышли! Нажмите "Регистрация", чтобы снова зарегистрироваться.',
                                        reply_markup=reply_markup)
    await query.answer("Произошла ошибка при удалении записей.")
    await query.answer("Все записи успешно удалены.")
    await query.edit_message_text("Вы удалили все записи и вышли из системы.")


# Обработчик кнопки "Выйти без удаления"
async def logout_without_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    unregister_user(user_id)

    keyboard = [['Регистрация']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text('Вы успешно вышли! Нажмите "Регистрация", чтобы снова зарегистрироваться.',
                                    reply_markup=reply_markup)

# Функция для отображения расписания
async def view_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    schedule = get_user_schedule(user_id)

    if not schedule:
        await update.message.reply_text("У вас нет записей в расписании.")
        return

    # Форматируем расписание в читабельный вид
    formatted_schedule = "\n".join(
        [f"{i+1}. {appointment.strftime('%d.%m.%Y %H:%M')}" for i, appointment in enumerate(schedule)]
    )

    # Отправляем пользователю
    await update.message.reply_text(f"Ваше расписание:\n{formatted_schedule}")

# Функция для создания Excel-файла с расписанием
def generate_schedule_excel(user_id, schedule):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Расписание"

    # Заголовок таблицы
    sheet.append(["№", "Дата и время"])

    # Заполнение данными
    for i, appointment in enumerate(schedule, start=1):
        sheet.append([i, appointment.strftime("%Y-%m-%d %H:%M")])

    # Сохранение в виртуальный файл
    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return output

# Функция для экспорта расписания
async def export_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    schedule = get_user_schedule(user_id)

    if not schedule or len(schedule) ==0 :
        await update.message.reply_text("У вас нет записей в расписании для экспорта.")
        return

    # Генерация Excel-файла
    excel_file = generate_schedule_excel(user_id, schedule)

    # Отправка файла пользователю
    await update.message.reply_document(
        document=InputFile(excel_file, filename=f"schedule_{user_id}.xlsx"),
        caption="Ваше расписание в формате Excel"
    )


# Основная функция
def main():
    app = Application.builder().token(TOKEN).build()

    # Обработчики команд
    app.add_handler(CommandHandler('start', start))

    # Обработчик кнопки регистрации
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex('Регистрация'), registration))

    # Обработчики кнопок для зарегистрированных пользователей
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex('Записаться на занятие'), schedule_trial))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex('Посмотреть расписание'), view_schedule))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex('Выйти'), logout))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex('Выгрузить расписание'), export_schedule))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex('Удалить запись на занятие'), delete_trial))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex('Выйти без удаления'), logout_without_delete))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex('Удалить все записи'), delete_all_records))
    app.add_handler(CallbackQueryHandler(delete_time, pattern=r'^delete_time_'))
    # Обработчик команды экспорта расписания
    #app.add_handler(CommandHandler('export_schedule', export_schedule))

    # Обработчики для выбора даты и времени
    app.add_handler(CallbackQueryHandler(choose_date, pattern=r'^choose_date_'))
    app.add_handler(CallbackQueryHandler(choose_time, pattern=r'^choose_time_'))

    # Запуск бота
    app.run_polling()

if __name__ == '__main__':
    main()
