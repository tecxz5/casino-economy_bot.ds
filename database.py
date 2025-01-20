import sqlite3
import datetime
import logging

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO, # Уровень логирования
    filename='bot_logs.log', # Имя файла для логов
    filemode='a', # Режим добавления новых записей в конец файла
    format='%(asctime)s:%(levelname)s:%(name)s: %(message)s', # Формат вывода логов
    encoding='utf-8' # Кодировка файла
)

def create_table():
    logging.info("Создание таблицы балансов")
    conn = sqlite3.connect('bot_balances.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS balances
                 (user_id INTEGER PRIMARY KEY, balance INTEGER)''')
    conn.commit()
    conn.close()
    logging.info("Таблица балансов создана")

def create_daily_bonus_table():
    logging.info("Создание таблицы ежедневного бонуса")
    conn = sqlite3.connect('bot_balances.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS daily_bonus
                 (user_id INTEGER PRIMARY KEY, last_daily DATE)''')
    conn.commit()
    conn.close()
    logging.info("Таблица ежедневного бонуса создана")

def create_donations_table():
    logging.info("Создание таблицы донатов")
    conn = sqlite3.connect('bot_balances.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS donations
                 (user_id INTEGER PRIMARY KEY, donation_amount INTEGER)''')
    conn.commit()
    conn.close()
    logging.info("Таблица донатов создана")

def daily_bonus(user_id):
    conn = sqlite3.connect('bot_balances.db')
    c = conn.cursor()
    today = datetime.datetime.now().date() # Получаем текущую дату как объект datetime.date

    # Проверяем, когда пользователь последний раз получал бонус
    c.execute('SELECT last_daily FROM daily_bonus WHERE user_id=?', (user_id,))
    last_daily_str = c.fetchone()

    if last_daily_str is None:
        # Если пользователь не получал бонус, обновляем его баланс
        c.execute('UPDATE balances SET balance=balance+100 WHERE user_id=?', (user_id,))
        c.execute(
            'INSERT INTO daily_bonus(user_id, last_daily) VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE SET last_daily=?',
            (user_id, today, today))
        conn.commit()
        conn.close()
        return True
    else:
        last_daily = datetime.datetime.strptime(last_daily_str[0], '%Y-%m-%d').date() # Преобразование строки в datetime.date
        if today > last_daily:
            # Если сегодня новый день и пользователь еще не получал бонус сегодня, обновляем его баланс
            c.execute('UPDATE balances SET balance=balance+100 WHERE user_id=?', (user_id,))
            c.execute('UPDATE daily_bonus SET last_daily=? WHERE user_id=?', (today, user_id))
            conn.commit()
            conn.close()
            return True
    conn.close()
    return False

def update_balance(user_id, amount):
    conn = sqlite3.connect('bot_balances.db')
    c = conn.cursor()
    # Проверяем, есть ли пользователь в базе, и обновляем баланс
    c.execute('SELECT balance FROM balances WHERE user_id=?', (user_id,))
    balance = c.fetchone()
    if balance:
        # Если пользователь уже есть в базе, обновляем его баланс
        # Используем разные запросы для увеличения и уменьшения баланса
        if amount >= 0:
            c.execute('UPDATE balances SET balance=balance+? WHERE user_id=?', (amount, user_id))
        else:
            # Для уменьшения баланса используем отрицательное значение amount
            c.execute('UPDATE balances SET balance=balance-? WHERE user_id=?', (-amount, user_id))
    else:
        # Если пользователя нет в базе, добавляем его с начальным балансом
        c.execute('INSERT INTO balances(user_id, balance) VALUES(?, ?)', (user_id, amount))
    conn.commit()
    conn.close()

def update_donation_amount(user_id, donation_amount):
    conn = sqlite3.connect('bot_balances.db')
    c = conn.cursor()
    # Проверяем, есть ли пользователь в таблице, и обновляем сумму пожертвований
    c.execute('SELECT donation_amount FROM donations WHERE user_id=?', (user_id,))
    result = c.fetchone()
    if result:
        # Если пользователь уже есть в таблице, обновляем его сумму пожертвований
        c.execute('UPDATE donations SET donation_amount=donation_amount+? WHERE user_id=?', (donation_amount, user_id))
    else:
        # Если пользователя нет в таблице, добавляем его с начальной суммой пожертвований
        c.execute('INSERT INTO donations(user_id, donation_amount) VALUES(?, ?)', (user_id, donation_amount))
    conn.commit()
    conn.close()

def deduct_donation(user_id, donation_amount):
    conn = sqlite3.connect('bot_balances.db')
    c = conn.cursor()
    # Проверяем, есть ли пользователь в базе, и обновляем баланс
    c.execute('SELECT balance FROM balances WHERE user_id=?', (user_id,))
    balance = c.fetchone()
    if balance:
        # Если пользователь уже есть в базе, обновляем его баланс
        new_balance = balance[0] - donation_amount
        if new_balance < 0:
            # Если баланс стал отрицательным, устанавливаем его равным 0
            new_balance = 0
        c.execute('UPDATE balances SET balance=? WHERE user_id=?', (new_balance, user_id))
    else:
        # Если пользователя нет в базе, добавляем его с начальным балансом
        c.execute('INSERT INTO balances(user_id, balance) VALUES(?, ?)', (user_id, 0))
    conn.commit()
    conn.close()

def get_balance(user_id):
    conn = sqlite3.connect('bot_balances.db')
    c = conn.cursor()
    c.execute('SELECT balance FROM balances WHERE user_id=?', (user_id,))
    balance = c.fetchone()
    conn.close()
    return balance[0] if balance else 0

def get_user_donation_amount(user_id):
    conn = sqlite3.connect('bot_balances.db')
    c = conn.cursor()
    # Запрос на выборку суммы пожертвований пользователя
    c.execute('SELECT donation_amount FROM donations WHERE user_id=?', (user_id,))
    result = c.fetchone()
    conn.close()
    # Если пользователь уже сделал пожертвования, возвращаем сумму, иначе возвращаем 0
    return result[0] if result else 0

def get_leaders():
    conn = sqlite3.connect('bot_balances.db')
    c = conn.cursor()
    c.execute('SELECT user_id, balance FROM balances ORDER BY balance DESC LIMIT 10')
    leaders = c.fetchall()
    conn.close()
    return leaders

def get_donation_leaders():
    conn = sqlite3.connect('bot_balances.db')
    c = conn.cursor()
    c.execute('SELECT user_id, donation_amount FROM donations ORDER BY donation_amount DESC LIMIT 10')
    leaders = c.fetchall()
    conn.close()
    return leaders

def set_initial_balance(user_id):
    conn = sqlite3.connect('bot_balances.db')
    c = conn.cursor()
    c.execute('''INSERT INTO balances(user_id, balance)
                 VALUES(?, ?)
                 ON CONFLICT(user_id) DO NOTHING''',
              (user_id, 500))
    conn.commit()
    conn.close()
