import psycopg2

# Данные для автоматического заполнения базы
info = [['Иван', 'Иванов', 'ii@mail.ru', ['86543214568', '85648545669', '82543696969']],
        ['Петр', 'Петров', 'pp@mail.ru', []],
        ['Алексей', 'Алексеев', 'aa@mail.ru',['86545252222']],
        ['Герасим', 'Герасимов', 'gg@mail.ru', ['82456895236', '87546953652']]]

def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS clients(
                    client_id   SERIAL      PRIMARY KEY,
                    first_name  VARCHAR(30) NOT NULL,   
                    last_name   VARCHAR(30) NOT NULL,
                    email       VARCHAR(30) NOT NULL UNIQUE
                    );
                    CREATE TABLE IF NOT EXISTS phones(
                    phone_id        SERIAL  PRIMARY KEY,
                    phone_number    VARCHAR(30) NOT NULL UNIQUE,    
                    client_id   INTEGER NOT NULL REFERENCES clients(client_id)
                    );
                    """)

        return 'В БД созданы таблицы "clients" и "phones"'


def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as cur:
        cur.execute("""
                    INSERT INTO clients (first_name, last_name, email) 
                            VALUES ('%s', '%s', '%s')
                            RETURNING client_id;
                    """ %(first_name, last_name, email))
        client = (cur.fetchone())
        client_id = client[0]
    if phones != None:
        for phone in phones:
            add_phone(conn, client_id, phone)
    return client_id


def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
                    INSERT INTO phones (phone_number, client_id) 
                            VALUES ('%s', '%s') RETURNING phone_id;
                    """ %(phone, client_id))
        id = (cur.fetchone())[0]
    return id


def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    with conn.cursor() as cur:
        if first_name != None:
            cur.execute("""
                        UPDATE clients SET first_name=%s WHERE client_id=%s;
                        """, (first_name, client_id))
            conn.commit()

        if last_name != None:
            cur.execute("""
                        UPDATE clients SET last_name=%s WHERE client_id=%s;
                        """, (last_name, client_id))
            conn.commit()

        if email != None:
            cur.execute("""
                        UPDATE clients SET email=%s WHERE client_id=%s;
                        """, (email, client_id))
            conn.commit()

        if phones != None:
            cur.execute("""
                        DELETE FROM phones WHERE client_id=%s;
                        """, (client_id,))
            conn.commit()
            for phone in phones:
                add_phone(conn, client_id, phone)


def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
                    DELETE FROM phones WHERE client_id=%s and phone_number=%s;
                    """, (client_id, phone))
        cur.execute("""
                    SELECT * FROM phones;
                    """)
        print(cur.fetchall())


def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
                       DELETE FROM phones WHERE client_id=%s;
                       """, (client_id,))
        cur.execute("""
               DELETE FROM clients WHERE client_id=%s;
               """, (client_id,))
        cur.execute("""
                    SELECT * FROM clients;
                    """)
        print(cur.fetchall())


def find_phone(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT phone_number FROM phones WHERE client_id=%s;
                    """, (client_id,))
        phones_tuple = cur.fetchall()
    phones = []
    for phone in phones_tuple:
        number = phone[0]
        phones.append(number)
    return phones


def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        if first_name != None:
            cur.execute("""
                        SELECT * FROM clients WHERE first_name=%s;
                        """, (first_name,))

        elif last_name != None:
            cur.execute("""
                        SELECT * FROM clients WHERE last_name=%s;
                        """, (last_name,))

        elif email != None:
            cur.execute("""
                        SELECT * FROM clients WHERE email=%s;
                        """, (email,))

        elif phone != None:
            cur.execute("""
                        SELECT client_id FROM phones WHERE phone_number=%s;
                        """, (phone,))
            client_id = (cur.fetchone())[0]
            cur.execute("""
                        SELECT * FROM clients WHERE client_id=%s;
                        """, (client_id,))
        client = list(cur.fetchone())
        client_id = client[0]
        client.append(find_phone(conn, client_id))
        return client




def bd_connect():
    with psycopg2.connect(database="client_base", user="postgre", password="postgre") as conn:
        print(create_db(conn))
        dialog(conn)
        # change_client(conn, 8, 'Vik', 'Трбер', 'vtriberauscads@i.ru', ('+79256544', '56489745321'))
        # print(find_client(conn, email='vtriber@gmail.ru'))
    conn.close()


def dialog(conn):
    print('Необходимо добавить данные о клиентах в базу данных')
    print('Для автоматического добавления данных введите 1 и нажмите enter')
    print('Для ввода данных вручную нажмите 2 и enter')
    key = input('Введите команду: ')
    if key == '1':
        for inf in info:
            first_name = inf[0]
            last_name = inf[1]
            mail = inf[2]
            phones = inf[3]
            if phones == []:
                add_client(conn, first_name, last_name, mail)
            else:
                add_client(conn, first_name, last_name, mail, phones)
    elif key == '2':
        while True:
            print('Введите данные клиента, если база заполнена введите "стоп"')
            first_name = input('Введите имя: ')
            if first_name == 'стоп':
                break
            last_name = input('Введите фамилию: ')
            mail = input('Введите адрес электронной почты: ')
            phones = []
            while True:
                phone = input('Введите номера телефона или "стоп" чтобы пропустить: ')
                if phone == '':
                    phone = input('Необходимо ввести номер телефона или "стоп" чтобы пропустить: ')
                if phone == 'стоп':
                    if phones == []:
                        add_client(conn, first_name, last_name, mail)
                    else:
                        add_client(conn, first_name, last_name, mail, phones)
                    break
                phones.append(phone)
        print()
        print('База данных заполнена')
        print()

    while True:
        print('Выберите команду для работы с базой данных')
        print('1 - добавить телефон для существующего клиента')
        print('2 - изменить данные о клиенте')
        print('3 - удалить телефон для существующего клиента')
        print('4 - удалить существующего клиента')
        print('5 - найти клиента по его данным')
        print('6 - остановить программу')
        print()
        key = input('Введите номер команды: ')
        if key == '1':
            client_id = input('Введите id клиента, для добавления телефона: ')
            phone = input('Введите номер телефона: ')
            print(add_phone(conn, client_id, phone))
        elif key == '2':
            first_name = None
            last_name = None
            client_id = input('Введите id клиента, для изменения данных: ')
            first_name = input('Введите новое имя (если не меняется нажмите enter)')
            if first_name == '': first_name = None
            last_name = input('Введите новую фамилию (если не меняется нажмите enter)')
            if last_name == '': last_name = None
            email = input('Введите новый электронный адрес (если не меняется нажмите enter)')
            if email == '': email = None
            phones = []
            while True:
                phone = input('Введите новый номер телефона или "стоп" чтобы пропустить: ')
                if phone == '':
                    phone = input('Необходимо ввести номер телефона или "стоп" чтобы пропустить: ')
                if phone == 'стоп':
                    if phones == []:
                        phones = None
                    break
                phones.append(phone)
            print(change_client(conn, client_id, first_name, last_name, email, phones))
        elif key == '3':
            client_id = input('Введите id клиента для удаления телефона: ')
            phone = input('Введите номер телефона для удаления: ')
            print(delete_phone(conn,client_id, phone))
            print()

        elif key == '4':
            client_id = input('Введите id клиента для удаления: ')
            print(delete_client(conn, client_id))
            print()

        elif key == '5':
            first_name = input('Введите имя для поиска(если не известно нажмите enter)')
            if first_name == '': first_name = None
            last_name = input('Введите фамилию для поиска (если не известна нажмите enter)')
            if last_name == '': last_name = None
            email = input('Введите электронный адрес для поиска (если не известен нажмите enter)')
            if email == '': email = None
            phone = input('Введите телефон для поиска (если не известен нажмите enter)')
            if phone == '': phone = None
            print(find_client(conn, first_name, last_name, email, phone))
            print()

        elif key == '6': break






if __name__ == '__main__':
    bd_connect()