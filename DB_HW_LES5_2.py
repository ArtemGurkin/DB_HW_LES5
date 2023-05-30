import psycopg2
import psycopg2.sql
from psycopg2.sql import SQL, Identifier


# Функция, создающая структуру БД (таблицы).

def create_table(conn):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS client(
    client_id SERIAL PRIMARY KEY,
    name VARCHAR (60) NOT NULL,
    surname VARCHAR (60) NOT NULL,
    email VARCHAR (60) NOT NULL UNIQUE
    );
    """)
    conn.commit()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS phone(
    phone_id SERIAL PRIMARY KEY,
    phone VARCHAR (60) NOT NULL UNIQUE,
    client_id INTEGER REFERENCES client(client_id)
    );
    """)
    conn.commit()

# Функция, позволяющая добавить нового клиента.

def add_client(conn, name, surname, email, phones=None):
    conn.execute("""INSERT INTO client(name, surname, email)
    VALUES(%s, %s, %s) RETURNING name, surname, client_id;""", (name, surname, email))
    return cur.fetchall()

# Функция, позволяющая добавить телефон для существующего клиента.

def add_phone(conn, phone, client_id):
    cur.execute("""
    INSERT INTO phone(phone, client_id)
    VALUES (%s, %s) RETURNING phone, client_id;
    """, (phone, client_id))
    return cur.fetchall()

# Функция, позволяющая изменить данные о клиенте.
def change_client(conn, client_id, name=None, surname=None, email=None):
    arg_list = {'name': name, 'surname': surname, 'email': email}
    for key, arg in arg_list.items():
        if arg:
            cur.execute(SQL("UPDATE client SET {}=%s WHERE client_id=%s").format(Identifier(key)), (arg, client_id))

    cur.execute("""
    SELECT * FROM client;
    """)
    return cur.fetchall()

# Функция, позволяющая удалить телефон для существующего клиента.

def delete_phone(conn, client_id, phone):
    cur.execute("""
    DELETE FROM phone WHERE client_id=%s AND phone=%s;
    """, (client_id, phone))

    cur.execute("""
    SELECT * FROM phone;
    """)
    return cur.fetchall()

# Функция, позволяющая удалить существующего клиента.

def delete_client(conn, client_id):
    cur.execute("""
    DELETE FROM phone WHERE client_id=%s;
    """, (client_id,))

    cur.execute("""
    DELETE FROM client WHERE client_id=%s;
    """, (client_id,))

    cur.execute("""
    SELECT * FROM client;
    """)
    return cur.fetchall()

# Функция, позволяющая найти клиента по его данным: имени, фамилии, email или телефону.

def find_client(conn, name=None, surname=None, email=None, phone=None):
    params = {}
    if name:
        params['name=%s'] = name
    if surname:
        params['surname=%s'] = surname
    if email:
        params['email=%s'] = email
    if phone:
        params['phone=%s'] = phone

    query = "SELECT * FROM client c JOIN phone ON c.client_id = phone.client_id WHERE " + ' and '.join(params) + ";"
    cur.execute(query, (*params.values(), ))
    return cur.fetchall()

with psycopg2.connect(database="DB_HW_LES2_2", user="artemgurkin", password="password") as conn:

    with conn.cursor() as cur:
        cur.execute("""
        DROP TABLE IF EXISTS phone;
        DROP TABLE IF EXISTS client;
        """)

    with conn.cursor() as cur:
        create_table(conn)

    with conn.cursor() as cur:
        print(add_client(cur, 'Иван', 'Иванов', 'ag@mail.ru'))

    with conn.cursor() as cur:
        print(add_phone(cur, '89997776655', '1'))

    with conn.cursor() as cur:
        print(change_client(cur, '1', surname='Petrov'))

    with conn.cursor() as cur:
        print(delete_phone(cur, '1', '89997776655'))

    with conn.cursor() as cur:
        print(delete_client(cur, '1'))

    with conn.cursor() as cur:
        print(find_client(cur, surname = 'Petrov'))

conn.close()

