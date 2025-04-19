from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db import get_db
from config import SUPER_ADMINS

def register_handlers(bot):
    @bot.message_handler(func=lambda m: m.text == "👨‍🍳 График бариста")
    def barista_menu(message: Message):
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT id, name FROM employees")
        employees = cur.fetchall()

        markup = InlineKeyboardMarkup()
        for emp_id, name in employees:
            markup.add(InlineKeyboardButton(name, callback_data=f"barista_view:{emp_id}"))

        bot.send_message(message.chat.id, "Выберите бариста для просмотра графика:", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("barista_view"))
    def show_barista_schedule(call: CallbackQuery):
        _, emp_id = call.data.split(":")
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT name FROM employees WHERE id = ?", (emp_id,))
        name = cur.fetchone()[0]

        cur.execute("SELECT date, shift FROM shifts WHERE employee_id = ? ORDER BY date", (emp_id,))
        shifts = cur.fetchall()

        if not shifts:
            text = f"У {name} нет назначенных смен."
        else:
            text = f"📅 График бариста {name}:\n"
            for date, shift in shifts:
                text += f"• {date} — {shift}\n"

        bot.edit_message_text(text, call.message.chat.id, call.message.message_id)

        if call.from_user.id in SUPER_ADMINS:
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("➕ Добавить смену", callback_data=f"barista_add:{emp_id}"),
                InlineKeyboardButton("➖ Удалить смену", callback_data=f"barista_del:{emp_id}")
            )
            bot.send_message(call.message.chat.id, "Управление графиком:", reply_markup=markup)

    # Добавление смены
    @bot.callback_query_handler(func=lambda call: call.data.startswith("barista_add"))
    def add_shift_start(call: CallbackQuery):
        _, emp_id = call.data.split(":")
        msg = bot.send_message(call.message.chat.id, "Введите дату смены (ГГГГ-ММ-ДД):")
        bot.register_next_step_handler(msg, lambda m: add_shift_date(m, emp_id))

    def add_shift_date(message: Message, emp_id):
        date = message.text.strip()
        msg = bot.send_message(message.chat.id, "Введите тип смены (например: Утро/Вечер):")
        bot.register_next_step_handler(msg, lambda m: save_shift(m, emp_id, date))

    def save_shift(message: Message, emp_id, date):
        shift = message.text.strip()
        db = get_db()
        cur = db.cursor()
        cur.execute("INSERT INTO shifts (employee_id, date, shift) VALUES (?, ?, ?)", (emp_id, date, shift))
        db.commit()
        bot.send_message(message.chat.id, "✅ Смена добавлена.")

    # Удаление смены
    @bot.callback_query_handler(func=lambda call: call.data.startswith("barista_del"))
    def delete_shift_start(call: CallbackQuery):
        _, emp_id = call.data.split(":")
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT id, date, shift FROM shifts WHERE employee_id = ?", (emp_id,))
        shifts = cur.fetchall()

        if not shifts:
            bot.send_message(call.message.chat.id, "У сотрудника нет смен.")
            return

        markup = InlineKeyboardMarkup()
        for shift_id, date, shift in shifts:
            markup.add(InlineKeyboardButton(f"{date} — {shift}", callback_data=f"shift_remove:{shift_id}"))
        bot.send_message(call.message.chat.id, "Выберите смену для удаления:", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("shift_remove"))
    def confirm_delete_shift(call: CallbackQuery):
        _, shift_id = call.data.split(":")
        db = get_db()
        cur = db.cursor()
        cur.execute("DELETE FROM shifts WHERE id = ?", (shift_id,))
        db.commit()
        bot.answer_callback_query(call.id, "Смена удалена.")
        bot.edit_message_text("❌ Смена удалена.", call.message.chat.id, call.message.message_id)
