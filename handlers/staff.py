from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db import get_db
from config import SUPER_ADMINS

def register_handlers(bot):
    @bot.message_handler(func=lambda m: m.text == "👥 Сотрудники")
    def show_employees(message: Message):
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT id, name, position, experience, status FROM employees")
        employees = cur.fetchall()

        if not employees:
            bot.send_message(message.chat.id, "Список сотрудников пуст.")
            return

        for emp in employees:
            emp_id, name, position, exp, status = emp
            text = (
                f"👤 <b>{name}</b>\n"
                f"🪪 Должность: {position}\n"
                f"📅 Стаж: {exp} лет\n"
                f"🔖 Статус: {status}"
            )
            markup = None
            if message.from_user.id in SUPER_ADMINS:
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("✏️ Редактировать", callback_data=f"emp_edit:{emp_id}"))
            bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=markup)

        if message.from_user.id in SUPER_ADMINS:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("➕ Добавить сотрудника", callback_data="emp_add"))
            bot.send_message(message.chat.id, "Управление сотрудниками:", reply_markup=markup)

    # ---------------- Добавление ----------------

    @bot.callback_query_handler(func=lambda call: call.data == "emp_add")
    def start_add_employee(call: CallbackQuery):
        msg = bot.send_message(call.message.chat.id, "Введите имя сотрудника:")
        bot.register_next_step_handler(msg, ask_position)

    def ask_position(message: Message):
        name = message.text.strip()
        msg = bot.send_message(message.chat.id, "Введите должность:")
        bot.register_next_step_handler(msg, lambda m: ask_experience(m, name))

    def ask_experience(message: Message, name):
        position = message.text.strip()
        msg = bot.send_message(message.chat.id, "Введите стаж (в годах):")
        bot.register_next_step_handler(msg, lambda m: ask_status(m, name, position))

    def ask_status(message: Message, name, position):
        experience = message.text.strip()
        msg = bot.send_message(message.chat.id, "Введите статус (активен / в отпуске / уволен):")
        bot.register_next_step_handler(msg, lambda m: save_employee(m, name, position, experience))

    def save_employee(message: Message, name, position, experience):
        status = message.text.strip()
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO employees (name, position, experience, status) VALUES (?, ?, ?, ?)",
            (name, position, experience, status)
        )
        db.commit()
        bot.send_message(message.chat.id, "✅ Сотрудник добавлен.")

    # ---------------- Редактирование ----------------

    @bot.callback_query_handler(func=lambda call: call.data.startswith("emp_edit"))
    def start_edit_employee(call: CallbackQuery):
        _, emp_id = call.data.split(":")
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT name, position, experience, status FROM employees WHERE id = ?", (emp_id,))
        emp = cur.fetchone()
        if not emp:
            bot.send_message(call.message.chat.id, "Сотрудник не найден.")
            return

        name, position, exp, status = emp
        msg = bot.send_message(call.message.chat.id, f"Новое имя ({name}):")
        bot.register_next_step_handler(msg, lambda m: edit_position(m, emp_id, name, position, exp, status))

    def edit_position(message: Message, emp_id, name, position, exp, status):
        new_name = message.text.strip() or name
        msg = bot.send_message(message.chat.id, f"Новая должность ({position}):")
        bot.register_next_step_handler(msg, lambda m: edit_experience(m, emp_id, new_name, position, exp, status))

    def edit_experience(message: Message, emp_id, name, position, exp, status):
        new_position = message.text.strip() or position
        msg = bot.send_message(message.chat.id, f"Новый стаж ({exp}):")
        bot.register_next_step_handler(msg, lambda m: edit_status(m, emp_id, name, new_position, exp, status))

    def edit_status(message: Message, emp_id, name, position, exp, status):
        new_exp = message.text.strip() or exp
        msg = bot.send_message(message.chat.id, f"Новый статус ({status}):")
        bot.register_next_step_handler(msg, lambda m: save_employee_edit(m, emp_id, name, position, new_exp))

    def save_employee_edit(message: Message, emp_id, name, position, experience):
        status = message.text.strip()
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "UPDATE employees SET name = ?, position = ?, experience = ?, status = ? WHERE id = ?",
            (name, position, experience, status, emp_id)
        )
        db.commit()
        bot.send_message(message.chat.id, "✅ Информация обновлена.")
