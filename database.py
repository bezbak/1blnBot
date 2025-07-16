import sqlite3
from contextlib import closing

def init_db():
    with closing(sqlite3.connect('bot.db')) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                lang TEXT DEFAULT '',
                is_subscribed BOOLEAN DEFAULT 0,
                is_registered BOOLEAN DEFAULT 0,
                last_message_id INTEGER
            )
        ''')
        conn.commit()

def get_user(user_id):
    with closing(sqlite3.connect('bot.db')) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return cursor.fetchone()

def create_user(user_id, lang=''):
    with closing(sqlite3.connect('bot.db')) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO users (user_id, lang) 
            VALUES (?, ?)
        """, (user_id, lang))
        conn.commit()

def update_user(user_id, **kwargs):
    with closing(sqlite3.connect('bot.db')) as conn:
        cursor = conn.cursor()
        set_clause = ", ".join([f"{key} = ?" for key in kwargs])
        values = list(kwargs.values())
        values.append(user_id)
        cursor.execute(f"""
            UPDATE users 
            SET {set_clause}
            WHERE user_id = ?
        """, values)
        conn.commit()

def save_message_id(user_id, message_id):
    update_user(user_id, last_message_id=message_id)

def get_message_id(user_id):
    user = get_user(user_id)
    return user[4] if user else None

def mark_user_registered(user_id: int):
    with sqlite3.connect("bot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_registered = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        
def is_user_authenticated(user_id:int):
    user = get_user(user_id)
    return True if user[3] else False

def is_user_has_lang(user_id:int):
    user = get_user(user_id)
    return user[1] if user[1] else False
    
def is_user_sub(user_id:int):
    user = get_user(user_id)
    return True if user[2] else False
    