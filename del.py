import sqlite3
import csv

# Подключаемся к базе данных SQLite
sqlite_conn = sqlite3.connect('db.sqlite3')
cursor = sqlite_conn.cursor()

# Получаем все имена таблиц
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Экспортируем каждую таблицу в CSV
for table in tables:
    table_name = table[0]

    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    # Записываем данные в CSV
    with open(f'{table_name}.csv', 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)

        # Получаем заголовки (имена столбцов)
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        writer.writerow(column_names)

        # Записываем данные
        writer.writerows(rows)

# Закрываем соединение с SQLite
sqlite_conn.close()
