import sqlite3

def init_db():
    conn = sqlite3.connect("coffee_bot.db")
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS shifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        barista TEXT,
        time TEXT,
        status TEXT
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS baristas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        schedule TEXT
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        address TEXT,
        contact TEXT,
        hours TEXT
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        position TEXT,
        experience TEXT,
        status TEXT
    )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
