import mariadb
import sys
from dotenv import load_dotenv
import os

load_dotenv()


def get_db_connection():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port_str = os.getenv("DB_PORT")
    database = os.getenv("DB_NAME")

    if not all([user, password, host, port_str, database]):
        raise ValueError("Missing required environment variables in .env file")

    assert port_str is not None
    port = int(port_str)

    conn = mariadb.connect(
        user=user, password=password, host=host, port=port, database=database
    )
    return conn


def get_cursor(conn):
    try:
        return conn.cursor()
    except mariadb.Error as e:
        print(f"Cursor creation error: {e}")
        return None


def close_db(conn, cursor=None):
    if cursor:
        try:
            cursor.close()
        except:
            pass
    if conn:
        try:
            conn.close()
        except:
            pass


def create_table():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to the database")
        sys.exit(1)
    cursor = get_cursor(conn)
    if not cursor:
        print("Failed to create cursor")
        close_db(conn)
        sys.exit(1)
    try:
        create_table_query = """ 
        create table if not exists users (
            id int auto_increment primary key,
            email varchar(255) unique,
            phone varchar(15) unique,
            otp varchar(4),
            verified boolean default false,
            created_at timestamp default current_timestamp
        )
        """
        cursor.execute(create_table_query)
        conn.commit()
        print("users table created successfully!")
    except mariadb.Error as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        close_db(conn, cursor)


def create_user_details_table():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to the database")
        sys.exit(1)
    cursor = get_cursor(conn)
    if not cursor:
        print("Failed to create a cursor")
        close_db(conn)
        sys.exit(1)
    try:
        create_user_table_query = """
            create table if not exists users_details (
            id int auto_increment primary key,
            ac_no int unique,
            name varchar(20),
            address varchar(255),
            email varchar(255) unique,
            phone varchar(15) unique,
            otp varchar(4),
            first_login boolean default true,
            created_at timestamp default current_timestamp
        )
        """
        cursor.execute(create_user_table_query)
        conn.commit()
        print("User details table created successfully")
    except mariadb.Error as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        close_db(conn, cursor)


def create_account_details():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to the database")
        sys.exit(1)
    cursor = get_cursor(conn)
    if not cursor:
        print("Failed to create cursor")
        close_db(conn)
        sys.exit(1)
    try:
        create_account_details_query = """
                create table if not exists account_details (
                ac_no int primary key,
                name varchar(20),
                balance float default 0,
                foreign key(ac_no) references users_details(ac_no)
        )
        """
        cursor.execute(create_account_details_query)
        conn.commit()
        print("Account Details table created successfully")
    except mariadb.Error as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        close_db(conn, cursor)


def create_table_deposit():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to the database")
        sys.exit(1)
    cursor = get_cursor(conn)
    if not cursor:
        print("Failed to create cursor")
        close_db(conn)
        sys.exit(1)
    try:
        create_table_deposit_query = """
        create table if not exists deposit(
            transaction_id int primary key,
            account_number int,
            deposit_type varchar(15),
            deposited_amount float,
            balance float,
            deposited_at timestamp default current_timestamp,
            foreign key(account_number) references account_details(ac_no)
        )
        """
        cursor.execute(create_table_deposit_query)
        conn.commit()
        print("deposits table created successfully!")
    except mariadb.Error as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        close_db(conn, cursor)


def create_cash_withdrawn():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to the database")
        sys.exit(1)
    cursor = get_cursor(conn)
    if not cursor:
        print("Failed to create cursor")
        close_db(conn)
        sys.exit(1)
    try:
        create_table_withdraw_query = """
        create table if not exists cash_withdrawn(
            transaction_id int primary key,
            account_number int,
            withdrawn_amount float,
            balance float,
            withdrawn_at timestamp default current_timestamp,
            foreign key(account_number) references account_details(ac_no)
        )
        """
        cursor.execute(create_table_withdraw_query)
        conn.commit()
        print("cash_withdrawn table created successfully!")
    except mariadb.Error as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        close_db(conn, cursor)


def create_table_send_money():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to the database")
        sys.exit(1)
    cursor = get_cursor(conn)
    if not cursor:
        print("Failed to create cursor")
        close_db(conn)
        sys.exit(1)
    try:
        create_table_send_money_query = """
        create table if not exists send_money(
            transaction_id int primary key,
            sender_account_no int,
            receiver_account_no int,
            amount_sent float,
            balance float,
            sent_at timestamp default current_timestamp,
            foreign key(sender_account_no) references account_details(ac_no),
            foreign key(receiver_account_no) references account_details(ac_no)
        )
        """
        cursor.execute(create_table_send_money_query)
        conn.commit()
        print("send money table created successfully!")
    except mariadb.Error as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        close_db(conn, cursor)


def create_transactions():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to the database")
        sys.exit(1)
    cursor = get_cursor(conn)
    if not cursor:
        print("Failed to create cursor")
        close_db(conn)
        sys.exit(1)
    try:
        create_transactions_query = """
                create table if not exists transactions (
                id int auto_increment primary key,
                transaction_id int ,
                account_no int ,
                transaction_type varchar(20),
                credit float,
                debit float,
                before_balance float,
                after_balance float,
                created_at timestamp default current_timestamp,
                foreign key(account_no) references account_details(ac_no)
        )
        """
        cursor.execute(create_transactions_query)
        conn.commit()
        print("transactions table created successfully")
    except mariadb.Error as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        close_db(conn, cursor)


if __name__ == "__main__":
    create_table()
    create_user_details_table()
    create_account_details()
    create_transactions()
    create_table_deposit()
    create_cash_withdrawn()
    create_table_send_money()
