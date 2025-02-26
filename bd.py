import psycopg2
import csv

# Установка соединения с базой данных PostgreSQL
conn_postgre = psycopg2.connect(
    dbname='CDEK_bots_data',
    host='26.150.48.237',
    port='5432',
    user='postgres',
    password='Cdek0001'
)

cur_postgre = conn_postgre.cursor()

# SQL-запрос для выборки данных из таблицы
select_query = "SELECT * FROM b2c_rfm_im_details;"  # Замените 'your_table_name' на фактическое имя вашей таблицы

cur_postgre.execute(select_query)

# Получить все строки из результата запроса
rows = cur_postgre.fetchall()

# Закрыть соединение и курсор с базой данных
cur_postgre.close()
conn_postgre.close()

# Запись данных в CSV файл
csv_file_path = 'output_data.csv'
with open(csv_file_path, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerows(rows)

print("Данные были успешно экспортированы в CSV файл:", csv_file_path)