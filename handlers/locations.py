from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db import get_db
from config import SUPER_ADMINS

def register_handlers(bot):
    @bot.message_handler(func=lambda m: m.text == "📍 Локации кофеен")
    def show_locations(message: Message):
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT id, name, address, contact, hours FROM locations")
        locations = cur.fetchall()

        if not locations:
            bot.send_message(message.chat.id, "Нет зарегистрированных кофеен.")
            return

        for loc in locations:
            loc_id, name, address, contact, hours = loc
            text = f"☕ <b>{name}</b>\n📍 Адрес: {address}\n🕐 Часы: {hours}\n📞 Контакты: {contact}"
            markup = None

            if message.from_user.id in SUPER_ADMINS:
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("✏️ Редактировать", callback_data=f"loc_edit:{loc_id}"))
            bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")

        if message.from_user.id in SUPER_ADMINS:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("➕ Добавить локацию", callback_data="loc_add"))
            bot.send_message(message.chat.id, "Управление локациями:", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data == "loc_add")
    def start_add_location(call: CallbackQuery):
        msg = bot.send_message(call.message.chat.id, "Введите название кофейни:")
        bot.register_next_step_handler(msg, ask_address)

    def ask_address(message: Message):
        name = message.text.strip()
        msg = bot.send_message(message.chat.id, "Введите адрес кофейни:")
        bot.register_next_step_handler(msg, lambda m: ask_contact(m, name))

    def ask_contact(message: Message, name):
        address = message.text.strip()
        msg = bot.send_message(message.chat.id, "Введите контактные данные (номер/Telegram):")
        bot.register_next_step_handler(msg, lambda m: ask_hours(m, name, address))

    def ask_hours(message: Message, name, address):
        contact = message.text.strip()
        msg = bot.send_message(message.chat.id, "Введите часы работы:")
        bot.register_next_step_handler(msg, lambda m: save_location(m, name, address, contact))

    def save_location(message: Message, name, address, contact):
        hours = message.text.strip()
        db = get_db()
        cur = db.cursor()
        cur.execute("INSERT INTO locations (name, address, contact, hours) VALUES (?, ?, ?, ?)",
                    (name, address, contact, hours))
        db.commit()
        bot.send_message(message.chat.id, "✅ Локация добавлена.")

    # ------------------ Редактирование ------------------

    @bot.callback_query_handler(func=lambda call: call.data.startswith("loc_edit"))
    def start_edit_location(call: CallbackQuery):
        _, loc_id = call.data.split(":")
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT name, address, contact, hours FROM locations WHERE id = ?", (loc_id,))
        loc = cur.fetchone()
        if not loc:
            bot.send_message(call.message.chat.id, "Локация не найдена.")
            return

        name, address, contact, hours = loc
        msg = bot.send_message(call.message.chat.id, f"Новое название ({name}):")
        bot.register_next_step_handler(msg, lambda m: edit_address(m, loc_id, name, address, contact, hours))

    def edit_address(message: Message, loc_id, name, address, contact, hours):
        new_name = message.text.strip() or name
        msg = bot.send_message(message.chat.id, f"Новый адрес ({address}):")
        bot.register_next_step_handler(msg, lambda m: edit_contact(m, loc_id, new_name, address, contact, hours))

    def edit_contact(message: Message, loc_id, name, address, contact, hours):
        new_address = message.text.strip() or address
        msg = bot.send_message(message.chat.id, f"Новые контакты ({contact}):")
        bot.register_next_step_handler(msg, lambda m: edit_hours(m, loc_id, name, new_address, contact, hours))

    def edit_hours(message: Message, loc_id, name, address, contact, hours):
        new_contact = message.text.strip() or contact
        msg = bot.send_message(message.chat.id, f"Новые часы работы ({hours}):")
        bot.register_next_step_handler(msg, lambda m: save_edited_location(m, loc_id, name, address, new_contact))

    def save_edited_location(message: Message, loc_id, name, address, contact):
        hours = message.text.strip()
        db = get_db()
        cur = db.cursor()
        cur.execute("""
            UPDATE locations SET name = ?, address = ?, contact = ?, hours = ?
            WHERE id = ?
        """, (name, address, contact, hours, loc_id))
        db.commit()
        bot.send_message(message.chat.id, "✅ Информация о локации обновлена.")
