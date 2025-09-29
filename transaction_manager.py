from db import get_db_connection, get_cursor, close_db
from transaction_id import TransactionId


class TransactionManager:
    def __init__(self):
        self.ti = TransactionId()
        pass

    def connection(self):
        conn = get_db_connection()
        if not conn:
            return None, None
        cursor = get_cursor(conn)
        if not cursor:
            close_db(conn)
            return None, None
        return conn, cursor

    def check_ac_no(self, ac_no):
        conn, cursor = self.connection()
        if conn is None or cursor is None:
            return None

        try:
            cursor.execute(
                """
                    SELECT ac_no 
                    FROM users_details
                    WHERE ac_no = %s;
                """,
                (ac_no,),
            )
            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            print(f"Database error retrieving details {e}")
            return None
        finally:
            close_db(conn, cursor)

    def get_account_balance(self, ac_no):
        conn, cursor = self.connection()
        if conn is None or cursor is None:
            return None

        try:
            cursor.execute(
                """
                    SELECT balance, status 
                    FROM account_details
                    WHERE ac_no = %s;
                """,
                (ac_no,),
            )
            result = cursor.fetchone()
            if result:
                return result[0], result[1]
        except Exception as e:
            print(f"Database error retrieving details {e}")
            return None
        finally:
            close_db(conn, cursor)

    def deposit(self, ac_no):
        print()
        print()
        print("===Choose Method of deposit===")
        print("1.Cash")
        print("2.Cheque")
        print("3.Demand Draft")
        choice = int(input("Enter Your Choice: "))
        deposit_type = ""
        while True:
            if choice == 1:
                deposit_type = "Cash"
                break
            elif choice == 2:
                deposit_type = "Cheque"
                break
            elif choice == 3:
                deposit_type = "DD"
                break
            else:
                print("Invalid Input")
                break
        try:
            amount = float(input("Enter the amount to deposit: "))
        except ValueError:
            print("Invalid input. Amount must be a number.")
            return None

        if amount < 100:
            print("Minimum deposit amount is 100.")
            return None
        transaction_id = self.ti.generate_transaction_id()
        conn, cursor = self.connection()
        if conn is None or cursor is None:
            return None
        try:
            cursor.execute(
                """
                    SELECT balance from account_details
                    where ac_no = %s """,
                (ac_no,),
            )
            result = cursor.fetchone()
            before_balance = result[0]
            new_balance = before_balance + amount
            cursor.execute(
                """
                    INSERT into deposit(transaction_id,account_number,deposit_type,deposited_amount,balance)
                    VALUES(%s,%s,%s,%s,%s)
                    """,
                (transaction_id, ac_no, deposit_type, amount, new_balance),
            )
            conn.commit()
        except Exception as e:
            print(f"Database Error: {e}")
            return None
        finally:
            close_db(conn, cursor)
        transaction_type = "Deposit"
        self.update_transaction_details(
            ac_no, transaction_id, amount, transaction_type, before_balance
        )
        self.update_account_details(ac_no, amount)
        return True

    def withdraw(self, ac_no):
        print()
        print()
        try:
            amount = float(input("Enter the amount to withdraw: "))
        except ValueError:
            print("Invalid input. Amount must be a number.")
            return None

        if amount < 50:
            print("Minimum withdrawal amount is 50.")
            return None
        transaction_id = self.ti.generate_transaction_id()
        conn, cursor = self.connection()
        if conn is None or cursor is None:
            return None
        try:
            cursor.execute(
                """
                    SELECT balance from account_details
                    where ac_no = %s """,
                (ac_no,),
            )
            result = cursor.fetchone()
            before_balance = result[0]
            if before_balance - amount < 1000:
                print(
                    "Insufficient balance. Minimum balance must be 1000 after withdrawal."
                )
                return None
            new_balance = before_balance - amount
            cursor.execute(
                """
                    INSERT into cash_withdrawn(transaction_id,account_number,withdrawn_amount,balance)
                    VALUES(%s,%s,%s,%s)
                    """,
                (transaction_id, ac_no, amount, new_balance),
            )
            conn.commit()
        except Exception as e:
            print(f"Database Error: {e}")
            return None
        finally:
            close_db(conn, cursor)
        transaction_type = "Withdraw"
        self.update_transaction_details(
            ac_no, transaction_id, amount, transaction_type, before_balance
        )
        self.update_account_details(ac_no, -amount)
        return True

    def send_money(self, ac_no):
        print()
        print()
        while True:
            receiver_ac_no = int(input("Enter 10 digit Receivers Account Number: "))
            if not self.check_ac_no(receiver_ac_no):
                print("The Receivers Account number Not found")
                continue
            else:
                break
        try:
            amount = float(input("Enter the amount to send: "))
        except ValueError:
            print("Invalid input. Amount must be a number.")
            return None
        if amount < 50:
            print("Minimum send amount is 50.")
            return False
        conn, cursor = self.connection()
        if conn is None or cursor is None:
            return
        try:
            cursor.execute(
                "SELECT balance FROM account_details WHERE ac_no = %s", (ac_no,)
            )
            sender_balance_result = cursor.fetchone()
            cursor.execute(
                "SELECT balance FROM account_details WHERE ac_no = %s",
                (receiver_ac_no,),
            )
            receiver_balance_result = cursor.fetchone()
            if (
                sender_balance_result
                and receiver_balance_result
                and sender_balance_result[0] - amount >= 1000
            ):
                transaction_id = self.ti.generate_transaction_id()
                sender_before_balance = sender_balance_result[0]
                receiver_before_balance = receiver_balance_result[0]
                new_sender_balance = sender_before_balance - amount
                cursor.execute(
                    "INSERT INTO send_money (transaction_id, sender_account_no, receiver_account_no, amount_sent, balance) VALUES (%s, %s, %s, %s, %s)",
                    (transaction_id, ac_no, receiver_ac_no, amount, new_sender_balance),
                )
                conn.commit()
                self.update_account_details(ac_no, -(amount))
                self.update_account_details(receiver_ac_no, amount)
                transaction_type = "Send Money"
                rec_transaction_type = "Deposit"
                self.update_transaction_details(
                    ac_no,
                    transaction_id,
                    amount,
                    transaction_type,
                    sender_before_balance,
                )
                self.update_transaction_details(
                    receiver_ac_no,
                    transaction_id,
                    amount,
                    rec_transaction_type,
                    receiver_before_balance,
                )
                print(
                    f"Sent {amount} to {receiver_ac_no}. New balance: {new_sender_balance}"
                )
                return True
            else:
                print(
                    "Insufficient balance. Minimum balance must be 1000 after sending, or invalid receiver."
                )
                return False
        except Exception as e:
            print(f"Error: {e}")
            conn.rollback()
            return False
        finally:
            close_db(conn, cursor)

    def update_account_details(self, ac_no, amount):
        conn, cursor = self.connection()
        if conn is None or cursor is None:
            return None
        try:
            cursor.execute(
                """ UPDATE account_details
                    SET name = (select name from users_details
                    where ac_no = %s),
                    balance = balance + %s
                    where ac_no=%s
                    """,
                (ac_no, amount, ac_no),
            )
            conn.commit()
        except Exception as e:
            print(f"Database Error: {e}")
            return None
        finally:
            close_db(conn, cursor)

    def update_transaction_details(
        self, ac_no, transaction_id, amount, transaction_type, before_balance
    ):
        conn, cursor = self.connection()
        if conn is None or cursor is None:
            return None
        try:
            if transaction_type == "Deposit":
                credit = amount
                debit = None
                after_balance = before_balance + amount
            elif transaction_type == "Send Money":
                credit = None
                debit = amount
                after_balance = before_balance - amount
            else:  # Withdraw
                debit = amount
                credit = None
                after_balance = before_balance - amount
            cursor.execute(
                """INSERT INTO transactions (transaction_id, account_no, transaction_type,credit,debit, before_balance, after_balance)
                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (
                    transaction_id,
                    ac_no,
                    transaction_type,
                    credit,
                    debit,
                    before_balance,
                    after_balance,
                ),
            )
            conn.commit()
        except Exception as e:
            print(f"Database Error: {e}")
            return None
        finally:
            close_db(conn, cursor)

    def activate_account(self, ac_no):
        print()
        print()
        print(
            "!!! Your Account is not active please Deposit Rs.1000 minimum to Activate your account"
        )
        self.deposit(ac_no)
        conn, cursor = self.connection()
        if conn is None or cursor is None:
            return None
        try:
            cursor.execute(
                """ UPDATE account_details
                    SET status = 'Active'
                    WHERE ac_no = %s
                    """,
                (ac_no,),
            )
            conn.commit()
        except Exception as e:
            print(f"Database Error: {e}")
            return None
        finally:
            close_db(conn, cursor)

    def get_transaction_history(self, ac_no):
        print()
        print()
        conn, cursor = self.connection()
        if conn is None or cursor is None:
            return None
        try:
            cursor.execute(
                """SELECT id, transaction_id, account_no, transaction_type, credit, debit, before_balance, after_balance, created_at 
                FROM transactions WHERE account_no =%s ORDER BY created_at DESC""",
                (ac_no,),
            )
            results = cursor.fetchall()
            history = []
            for row in results:
                to_ac_no = None
                if row[3] == "Send Money":
                    cursor.execute(
                        "SELECT receiver_account_no FROM send_money WHERE transaction_id = %s",
                        (row[1],),
                    )  # transaction_id
                    receiver = cursor.fetchone()
                    to_ac_no = receiver[0] if receiver else None

                history.append(
                    {
                        "id": row[0],
                        "transaction_id": row[1],
                        "account_no": row[2],
                        "type": row[3],
                        "credit": row[4] or 0.0,
                        "debit": row[5] or 0.0,
                        "before_balance": row[6] or 0.0,
                        "after_balance": row[7] or 0.0,
                        "date": row[8],
                        "to_ac_no": to_ac_no,
                    }
                )
            return history
        except Exception as e:
            print(f"Database error: {e}")
            return None
        finally:
            close_db(conn, cursor)

    def temp_update_account_details(self, ac_no):
        conn, cursor = self.connection()
        if conn is None or cursor is None:
            return None
        try:
            cursor.execute(
                "SELECT ac_no FROM account_details WHERE ac_no = %s", (ac_no,)
            )
            if cursor.fetchone():
                return  # already exists
            cursor.execute("SELECT name FROM users_details WHERE ac_no = %s", (ac_no,))
            result = cursor.fetchone()
            name = result[0] if result else "Unknown"
            cursor.execute(
                """
                    insert into account_details(ac_no, name, balance, status)
                    values(%s, %s, %s, %s)
                """,
                (ac_no, name, 0, "Inactive"),
            )
            conn.commit()
        except Exception as e:
            print(f"Database error: {e}")
            conn.rollback()
            return None
        finally:
            close_db(conn, cursor)
