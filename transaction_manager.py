import mariadb
from db import get_db_connection, get_cursor, close_db

class TransactionManager:
    def __init__(self):
        pass
    def connection(self):
        conn = get_db_connection()
        if not conn:
            return None,None
        cursor = get_cursor(conn)
        if not cursor:
            close_db(conn)
            return None,None
        return conn, cursor

        
    def temp_update_account_details(self,ac_no):
        conn , cursor = self.connection()
        if conn is None or cursor is None:
            return None
        try:
            cursor.execute(
                """ 
                    insert into account_details(ac_no,balance)
                    values(%s,%s)
                """,(ac_no,0)
                    )
            conn.commit()
        except Exception as e:
            print(f"Database error: {e}")
            conn.rollback()
            return None
        finally:
            close_db(conn, cursor)

            

