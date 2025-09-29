from db import get_db_connection, get_cursor, close_db
class TransactionId:
    def __init__(self):
        pass

    def generate_transaction_id(self):
        conn = get_db_connection()
        if not conn:
            return None

        cursor = get_cursor(conn)
        if not cursor:
            close_db(conn)
            return None

        try:
            transaction_id = 1000001

            while True:
                cursor.execute("""
                    SELECT transaction_id FROM transactions
                    WHERE transaction_id = %s
                """, (transaction_id,))

                if not cursor.fetchone():
                    return transaction_id
                transaction_id += 1

        except Exception as e:
            print(f"Error generating Transaction Id: {e}")
            return None

        finally:
            close_db(conn, cursor)



