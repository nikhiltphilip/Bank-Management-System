import mariadb
from db import get_db_connection, get_cursor, close_db


class DatabaseManager:
    def __init__(self):
        pass

    def check_existing_user(self, email=None, phone=None):
        conn = get_db_connection()
        if not conn:
            return None
        cursor = get_cursor(conn)
        if not cursor:
            close_db(conn)
            return None
        try:
            if email:
                cursor.execute("select id from users where email = %s", (email,))
            elif phone:
                cursor.execute("select id from users where phone = %s", (phone,))

            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            print(f"Database error: {e}")
            return False
        finally:
            close_db(conn, cursor)

    def first_login(self, email=None, phone=None):
        conn = get_db_connection()
        if not conn:
            return None
        cursor = get_cursor(conn)
        if not cursor:
            close_db(conn)
            return None
        try:
            if email:
                cursor.execute(
                    "select first_login from users_details where email = %s", (email,)
                )
            elif phone:
                cursor.execute(
                    "select first_login from users_details  where phone = %s", (phone,)
                )
            result = cursor.fetchone()
            return result[0]
        except Exception as e:
            print(f"Database error: {e}")
            return False
        finally:
            close_db(conn, cursor)
    

    def save_user_temp(self, email=None, phone=None, otp=None):
        conn = get_db_connection()
        if not conn:
            return None
        cursor = get_cursor(conn)
        if not cursor:
            close_db(conn)
            return None
        try:
            cursor.execute(
                """
                            replace into users (email,phone,otp,verified)
                            values (%s,%s,%s,False)
                    """,
                (email, phone, otp),
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Database error: {e}")
            return None
        finally:
            close_db(conn, cursor)

    def save_users_details_temp(self, email=None, phone=None, otp=None):
        conn = get_db_connection()
        if not conn:
            return None
        cursor = get_cursor(conn)
        if not cursor:
            close_db(conn)
            return None
        try:
            cursor.execute(
                """
                           update users_details set otp = %s 
                           where email = %s or phone = %s
                    """,
                (otp, email, phone),
            )
            cursor.execute(
                "SELECT id FROM users_details WHERE email = %s OR phone = %s",
                (email, phone),
            )
            result = cursor.fetchone()

            conn.commit()
            return result[0] if result else None
        except Exception as e:
            print(f"Database error: {e}")
            return None
        finally:
            close_db(conn, cursor)

    def verify_and_update_user(self, user_id, entered_otp):
        conn = get_db_connection()

        if not conn:
            return None
        cursor = get_cursor(conn)

        if not cursor:
            close_db(conn)
            return None
        try:
            cursor.execute("select otp from users where id =%s", (user_id,))
            result = cursor.fetchone()

            if result and result[0] == entered_otp:
                cursor.execute(
                    """ update users set verified = TRUE ,otp = NULL
                    where id = %s
                        """,
                    (user_id,),
                )
                conn.commit()
                return True
            else:
                return False
        except Exception as e:
            print(f"Database Error: {e}")
            return False
        finally:
            close_db(conn, cursor)

    def verify_user_details(self, user_id, entered_otp):
        conn = get_db_connection()

        if not conn:
            return None
        cursor = get_cursor(conn)

        if not cursor:
            close_db(conn)
            return None
        try:
            cursor.execute("select otp from users_details where id =%s", (user_id,))
            result = cursor.fetchone()

            if result and result[0] == entered_otp:
                cursor.execute(
                    """ update users_details set otp = NULL
                    where id = %s
                        """,
                    (user_id,),
                )
                conn.commit()
                return True
            else:
                return False
        except Exception as e:
            print(f"Database Error: {e}")
            return False
        finally:
            close_db(conn, cursor)

    def update_users_details(self,details,user_id):
        if not details or not user_id:
            print("Invalid input: details or user_id missing")
            return False

        required_fields = ['name', 'address', 'mobile', 'email', 'ac_no']
        if not all(field in details for field in required_fields):
            print("Invalid input: missing required fields")
            return False
        conn = get_db_connection()
        if not conn:
            return None
        cursor = get_cursor(conn)
        if not cursor:
            close_db(conn)
            return None
        try:

            name = details.get('name')
            address = details.get('address')
            mobile = details.get('mobile')
            email = details.get('email')
            ac_no = details.get('ac_no')
            
            cursor.execute("""
                                update users_details
                                set name = %s,address = %s,phone = %s,email = %s,
                                ac_no = %s, first_login = %s
                                where id = %s
                                """,(name,address,mobile,email,ac_no,False,user_id))
            cursor.execute("""
                            update users 
                            set email = %s, phone = %s
                            where email = %s or phone = %s
                            """,(email,mobile,email,mobile))
            conn.commit()
            print("User details updated successfully")
        except mariadb.Error as e:
            print(f"Database error updating user details: {e}")
            conn.rollback()  # Rollback on error

            return False
        finally:
            close_db(conn, cursor)

    def insert_user_details(self, email=None, phone=None):
        conn = get_db_connection()
        if not conn:
            return None
        cursor = get_cursor(conn)
        if not cursor:
            close_db(conn)
            return None
        try:
            cursor.execute(
                """
                                insert into users_details(email,phone)
                                values(%s,%s)
                                """,
                (email, phone),
            )
            conn.commit()
        except Exception as e:
            print(f"Database error: {e}")
            return None
        finally:
            close_db(conn, cursor)
    
    def display_details(self,user_id):
        conn = get_db_connection()
        if not conn:
            return None
        cursor = get_cursor(conn)
        if not cursor:
            close_db(conn)
            return None
        try:
            cursor.execute("""
                            select ac_no, name, address,
                            phone,email,created_at from users_details
                            where id =%s
                            """,(user_id,))
            result = cursor.fetchone()
            if result:
                return {
                'ac_no': result[0],
                'name': result[1],
                'address': result[2],
                'phone': result[3],
                'email': result[4],
                'created_at': result[5]
            }
            else:
              return None

        except Exception as e:
            print(f"Database error retrieving user details: {e}")
            return None
        finally:
            close_db(conn, cursor)


    def delete_failed_registration(self, user_id):
        conn = get_db_connection()
        if not conn:
            return None
        cursor = get_cursor(conn)
        if not cursor:
            close_db(conn)
            return None
        try:
            cursor.execute("""delete from users where id = %s""", (user_id,))
            conn.commit()
        except Exception as e:
            print(f"Database Error: {e}")
            return False
        finally:
            close_db(conn, cursor)
