import mariadb
import traceback
import sys


def get_db_connection():
    try:
        conn = mariadb.connect(
            user="null", password="1234", host="localhost", port=3306, database="bank"
        )
        return conn
    except mariadb.Error as e:
        print(f"Database connection error: {e}")
        traceback.print_exc()
        return None


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

if __name__ == "__main__":
    create_table()
    create_user_details_table()
