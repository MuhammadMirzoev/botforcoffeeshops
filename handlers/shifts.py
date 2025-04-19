from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db import get_db
from config import SUPER_ADMINS

def register_handlers(bot):
    @bot.message_handler(func=lambda m: m.text == "📅 График смен")
    def show_shift_menu(message: Message):
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.row(KeyboardButton("🔍 Посмотреть смену"), KeyboardButton("🔄 Запросить изменение"))
        kb.row(KeyboardButton("🔙 Назад"))
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=kb)

    @bot.message_handler(func=lambda m: m.text == "🔍 Посмотреть смену")
    def ask_date(message: Message):
        bot.send_message(message.chat.id, "Введите дату в формате ГГГГ-ММ-ДД для просмотра смен:")
        bot.register_next_step_handler(message, show_shifts_by_date)

    def show_shifts_by_date(message: Message):
        date = message.text.strip()
        db = get_db()
        cur = db.cursor()
        cur.execute("""
            SELECT e.name, s.shift FROM shifts s
            JOIN employees e ON s.employee_id = e.id
            WHERE s.date = ?
        """, (date,))
        results = cur.fetchall()
        if results:
            text = f"Смены на {date}:\n"
            for name, shift in results:
                text += f"👤 {name} — {shift}\n"
        else:
            text = "Смен на эту дату не найдено."
        bot.send_message(message.chat.id, text)

    @bot.message_handler(func=lambda m: m.text == "🔄 Запросить изменение")
    def ask_shift_change_date(message: Message):
        bot.send_message(message.chat.id, "Введите дату смены, которую хотите изменить (ГГГГ-ММ-ДД):")
        bot.register_next_step_handler(message, ask_shift_change_reason)

    def ask_shift_change_reason(message: Message):
        date = message.text.strip()
        user_id = message.from_user.id
        db = get_db()
        cur = db.cursor()
        # Получаем сотрудника по user_id (временно: ищем по Telegram ID как phone для простоты)
        cur.execute("SELECT id FROM employees WHERE phone = ?", (str(user_id),))
        employee = cur.fetchone()
        if not employee:
            bot.send_message(message.chat.id, "Вы не зарегистрированы как сотрудник.")
            return
        employee_id = employee[0]

        def get_reason(msg: Message):
            reason = msg.text.strip()
            cur.execute("INSERT INTO shift_requests (employee_id, date, reason) VALUES (?, ?, ?)",
                        (employee_id, date, reason))
            db.commit()
            bot.send_message(message.chat.id, "Ваш запрос отправлен на рассмотрение.")
            notify_admins_shift_request(bot, employee_id, date, reason)

        bot.send_message(message.chat.id, "Укажите причину запроса:")
        bot.register_next_step_handler(message, get_reason)

    def notify_admins_shift_request(bot, employee_id, date, reason):
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT name FROM employees WHERE id = ?", (employee_id,))
        name = cur.fetchone()[0]

        for admin in SUPER_ADMINS:
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("✅ Одобрить", callback_data=f"shift_accept:{employee_id}:{date}"),
                InlineKeyboardButton("❌ Отклонить", callback_data=f"shift_reject:{employee_id}:{date}")
            )
            bot.send_message(admin, f"Запрос на изменение смены от {name} на {date}.\nПричина: {reason}", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("shift_"))
    def handle_shift_callback(call: CallbackQuery):
        action, emp_id, date = call.data.split(":")
        db = get_db()
        cur = db.cursor()

        if action == "shift_accept":
            cur.execute("UPDATE shift_requests SET status = 'approved' WHERE employee_id = ? AND date = ?", (emp_id, date))
            bot.answer_callback_query(call.id, "Запрос одобрен.")
            bot.edit_message_text("✅ Запрос одобрен.", call.message.chat.id, call.message.message_id)
        elif action == "shift_reject":
            cur.execute("UPDATE shift_requests SET status = 'rejected' WHERE employee_id = ? AND date = ?", (emp_id, date))
            bot.answer_callback_query(call.id, "Запрос отклонён.")
            bot.edit_message_text("❌ Запрос отклонён.", call.message.chat.id, call.message.message_id)

        db.commit()
