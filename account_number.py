from db import get_db_connection, get_cursor, close_db
class AccountNumber:
    def __init__(self):
        pass

    def generate_account_number(self):
        conn = get_db_connection()
        if not conn:
            return None

        cursor = get_cursor(conn)
        if not cursor:
            close_db(conn)
            return None

        try:
            account_number = 10000000001

            while True:
                cursor.execute("""
                    SELECT ac_no FROM users_details
                    WHERE ac_no = %s
                """, (account_number,))

                if not cursor.fetchone():
                    return account_number
                account_number += 1

        except Exception as e:
            print(f"Error generating account number: {e}")
            return None

        finally:
            close_db(conn, cursor)


