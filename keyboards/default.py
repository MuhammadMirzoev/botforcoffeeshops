from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        KeyboardButton("📅 График смен"),
        KeyboardButton("👤 График бариста"),
    )
    markup.add(
        KeyboardButton("📍 Локации кофеен"),
        KeyboardButton("👥 Сотрудники"),
    )
    markup.add(
        KeyboardButton("⚙️ Настройки"),
    )
    return markup

def admin_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        KeyboardButton("➕ Добавить смену"),
        KeyboardButton("📋 Все смены"),
    )
    markup.add(
        KeyboardButton("📍 Локации кофеен"),
        KeyboardButton("👥 Сотрудники"),
    )
    return markup
