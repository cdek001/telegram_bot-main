import sqlite3
import os

# Убедитесь, что путь к базе данных корректен.
db_path = './data/users.db'  # Замените на ваш путь к базе данных

# Проверяем, существует ли файл базы данных
if not os.path.exists(db_path):
    print(f"Database file '{db_path}' does not exist.")
else:
    # Подключаемся к базе данных
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Выводим список всех таблиц в базе данных
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    if tables:
        print("Tables in the database:")
        for table_name in tables:
            print(f"- {table_name[0]}")

            # Выводим все данные из текущей таблицы
            cursor.execute(f"SELECT * FROM {table_name[0]};")
            rows = cursor.fetchall()

            # Печатаем строки таблицы
            for row in rows:
                print(row)

            print("\n")
    else:
        print("No tables found in the database.")

    # Закрываем соединение
    conn.close()