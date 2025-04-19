import os

structure = {
    'coffee_bot': [
        'bot.py',
        'config.py',
        'create_project.py',
        'database/db.py',
        'handlers/base.py',
        'handlers/shifts.py',
        'handlers/barista.py',
        'handlers/locations.py',
        'handlers/staff.py',
        'keyboards/default.py',
        'models/schema.py'
    ]
}

base_code = {
    'bot.py': '''from telebot import TeleBot
from config import TOKEN
from handlers import base, shifts, barista, locations, staff

bot = TeleBot(TOKEN)

base.register_handlers(bot)
shifts.register_handlers(bot)
barista.register_handlers(bot)
locations.register_handlers(bot)
staff.register_handlers(bot)

if __name__ == "__main__":
    bot.polling(none_stop=True)
''',

    'config.py': '''TOKEN = "YOUR_BOT_TOKEN_HERE"
SUPER_ADMINS = [123456789]  # Вставь сюда свой user_id
''',

    'database/db.py': '''import sqlite3
from models.schema import CREATE_TABLES

def get_db():
    return sqlite3.connect("coffee_bot/database/coffee.db", check_same_thread=False)

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    for query in CREATE_TABLES:
        cursor.execute(query)
    conn.commit()
    conn.close()

init_db()
''',

    'models/schema.py': '''CREATE_TABLES = [
    """
    CREATE TABLE IF NOT EXISTS admins (
        user_id INTEGER PRIMARY KEY
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        position TEXT,
        experience INTEGER,
        status TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS shifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        date TEXT,
        shift TEXT,
        FOREIGN KEY (employee_id) REFERENCES employees(id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        address TEXT,
        contact TEXT,
        work_hours TEXT
    );
    """
]
''',

    'handlers/base.py': '''from telebot.types import Message
from keyboards.default import main_menu
from config import SUPER_ADMINS

def register_handlers(bot):
    @bot.message_handler(commands=["start"])
    def start(message: Message):
        bot.send_message(message.chat.id, "Добро пожаловать в кофейного бота ☕️", reply_markup=main_menu())
''',

    'keyboards/default.py': '''from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("📅 График смен"), KeyboardButton("👨‍🍳 График бариста"))
    kb.row(KeyboardButton("📍 Локации"), KeyboardButton("👥 Сотрудники"))
    kb.row(KeyboardButton("⚙️ Настройки"))
    return kb
''',

    'handlers/shifts.py': 'def register_handlers(bot): pass\n',
    'handlers/barista.py': 'def register_handlers(bot): pass\n',
    'handlers/locations.py': 'def register_handlers(bot): pass\n',
    'handlers/staff.py': 'def register_handlers(bot): pass\n'
}

def create_structure():
    for root, files in structure.items():
        for file_path in files:
            full_path = os.path.join(file_path)
            dir_path = os.path.dirname(full_path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path)
            if not os.path.exists(full_path):
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(base_code.get(os.path.basename(full_path), ''))

    print("✅ Структура проекта создана. Заполни config.py своим токеном и запусти bot.py")

if __name__ == "__main__":
    create_structure()
