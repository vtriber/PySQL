import psycopg2


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

with psycopg2.connect(database="client_base", user="vtriber", password="SuperPython43") as conn:
    print(create_db(conn))
    # change_client(conn, 8, 'Vik', 'Трбер', 'vtriberauscads@i.ru', ('+79256544', '56489745321'))
    # print(find_client(conn, email='vtriber@gmail.ru'))
conn.close()



if __name__ == '__main__':