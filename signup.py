import time
from validators import UserValidator
from otp import OtpManager
from database_manager import DatabaseManager
from account_number import AccountNumber
from transaction_manager import TransactionManager

OTP_EXPIRY_TIME = 30


class Signup:
    def __init__(self):
        self.validator = UserValidator()
        self.db = DatabaseManager()
        self.otp_manager = OtpManager()
        self.ac = AccountNumber()
        self.tm = TransactionManager()

    def display(self):
        print("==== CLI Based Bank Management System ====")
        print("1.Signup")
        print("2.Login")
        print("3.Exit")

    def get_inputs(self):
        while True:
            user_input = input("Email/Phone: ").strip()

            if not user_input:
                print("Enter a valid Email or Phone No")
                continue
            if "@" in user_input:
                if not self.validator.validate_email(user_input):
                    print("Invalid Email address , Please try again")
                    continue
                return user_input, None, "email"
            else:
                if not self.validator.validate_phone(user_input):
                    print("Invalid phone number, Please try again")
                    continue
                return None, user_input, "phone"

    def process_signup(self):
        print("=== CLI Signup System===")
        print("Enter your email or phone number to signup: ")
        email, phone, input_type = self.get_inputs()

        if self.db.check_existing_user(email=email, phone=phone):
            print("Already registered! Please login for further process.")
            return
        while True:
            otp = self.otp_manager.generate_otp()
            print(f"\nOTP sent to your {input_type}: {otp}")
            print("Please enter the 4-digit OTP:")

            user_id = self.db.save_user_temp(email=email, phone=phone, otp=otp)

            if not user_id:
                print("Error saving user data, Please try again.")
                return
            start_time = time.time()
            entered_otp = input("Otp: ").strip()
            end_time = time.time()
            elapsed_time = end_time - start_time
            if elapsed_time > OTP_EXPIRY_TIME:
                print("OTP Expired ")
                continue
            if self.db.verify_and_update_user(user_id, entered_otp):
                print(
                    "\nRegistration successful! You can now login for further process."
                )
                self.db.insert_user_details(email=email, phone=phone)
                break
            else:
                print("Invalid OTP. Please try again.")
                self.db.delete_failed_registration(user_id)
                continue

    def collect_user_detail(self, email=None, phone=None):
        print("== First time login please fill the below details ==")
        verified_email = email
        verified_phone = phone

        print(f"Verified Email: {verified_email or 'Not provided'}")
        print(f"Verified Phone: {verified_phone or 'Not provided'}")
        print()

        while True:
            name = input("Full Name: ").strip()
            address = input("Address: ").strip()

            if verified_phone:
                print(f"Mobile Number (verified): {verified_phone}")
                mobile = verified_phone
            else:
                mobile = input("Mobile Number: ").strip()

            if verified_email:
                print(f"Email (verified): {verified_email}")
                email = verified_email
            else:
                email = input("Email: ").strip()

            if not name:
                print("Name is required.")
                continue

            if not address:
                print("Address is required.")
                continue

            if not mobile or not self.validator.validate_phone(mobile):
                print("Valid mobile number is required.")
                continue

            if not email or not self.validator.validate_email(email):
                print("Valid email is required.")
                continue

            print("\n--- Entered Details ---")
            print(f"Name: {name}")
            print(f"Address: {address}")
            print(f"Mobile: {mobile}")
            print(f"Email: {email}")

            confirm = (
                input("\nAll details entered correctly? (yes/no): ").strip().lower()
            )

            if confirm == "yes":
                ac_no = self.ac.generate_account_number()
                return {
                    "name": name,
                    "address": address,
                    "mobile": mobile,
                    "email": email,
                    "ac_no": ac_no,
                }
            else:
                print("Let's try again.")
                continue

    def process_transaction(self, user_details):
        if user_details:
            ac_no = user_details["ac_no"]
            self.tm.temp_update_account_details(ac_no)
            result = self.tm.get_account_balance(ac_no)
            if not result:
                print("Account data unavailable.")
                return
            balance, status = result
            if balance < 1000 and status == "Inactive":
                self.tm.activate_account(ac_no)
            while True:
                print()
                print()
                print("===Transaction Menu===")
                print("1.Deposit")
                print("2.Withdraw")
                print("3.Send Money")
                print("4.Check Balance")
                print("5.List Last 10 Transactions")
                print("6.Logout")

                choice = input("Enter choice (1-6): ").strip()
                if choice == "1":
                    self.tm.deposit(ac_no)
                elif choice == "2":
                    self.tm.withdraw(ac_no)
                elif choice == "3":
                    self.tm.send_money(ac_no)
                elif choice == "4":
                    result = self.tm.get_account_balance(ac_no)
                    if result:
                        balance, status = result
                        print(f"Your current balance is: {balance}")
                        print(f"Account status: {status}")
                    else:
                        print("Unable to retrieve balance.")
                elif choice == "5":
                    history = self.tm.get_transaction_history(ac_no)
                    if history:
                        print("Transaction History:")
                        # Headers
                        print(f"{'ID':<5} {'Txn ID':<10} {'Type':<12} {'Credit':<10} {'Debit':<10} {'Before Bal':<12} {'After Bal':<12} {'Date':<20} {'To Ac No':<10}")
                        print("-" * 110)
                        for trans in history[-10:]:  # last 10
                            print(f"{trans['id']:<5} {trans['transaction_id']:<10} {trans['type']:<12} {trans.get('credit', 0):<10.2f} {trans.get('debit', 0):<10.2f} {trans['before_balance']:<12.2f} {trans['after_balance']:<12.2f} {str(trans['date']):<20} {trans['to_ac_no'] or '':<10}")
                    else:
                        print("No transactions found.")
                elif choice == "6":
                    break
                else:
                    print("Invalid Input.")

    def process_login(self):
        print("=== CLI Login System ===")
        print("Enter your Registered email of phone number to Login: ")
        email, phone, input_type = self.get_inputs()

        if not self.db.check_existing_user(email=email, phone=phone):
            print("Not registered ! please Signup.")
            return
        while True:
            otp = self.otp_manager.generate_otp()
            print(f"\nOTP sent to your {input_type}: {otp}")
            print("Please enter the 4-digit OTP: ")
            user_id = self.db.save_users_details_temp(email=email, phone=phone, otp=otp)
            if not user_id:
                print("Error saving user data, Please try again.")
                return
            start_time = time.time()
            entered_otp = input("Otp: ").strip()
            end_time = time.time()
            elapsed_time = end_time - start_time

            if elapsed_time > OTP_EXPIRY_TIME:
                print("OTP Expired")
                continue

            if self.db.verify_user_details(user_id, entered_otp):
                print("\n Login successful!")
                if self.db.first_login(email=email, phone=phone):
                    details = self.collect_user_detail(email=email, phone=phone)
                    self.db.update_users_details(details, user_id)
                    user_details = self.db.display_details(user_id)
                    if user_details:
                        print("=== User Profile ===")
                        print(f"Account Number: {user_details['ac_no']}")
                        print(f"Name: {user_details['name']}")
                        print(f"Address: {user_details['address']}")
                        print(f"Phone: {user_details['phone']}")
                        print(f"Email: {user_details['email']}")
                        print(f"Member Since: {user_details['created_at']}")
                    else:
                        print("User details not found")
                else:
                    user_details = self.db.display_details(user_id)
                    name = user_details.get("name") if user_details else "User"
                    print(f"Welcome back {name}")
                    if user_details:
                        print("=== User Profile ===")
                        print(f"Account Number: {user_details['ac_no']}")
                        print(f"Name: {user_details['name']}")
                        print(f"Address: {user_details['address']}")
                        print(f"Phone: {user_details['phone']}")
                        print(f"Email: {user_details['email']}")
                        print(f"Member Since: {user_details['created_at']}")
                    else:
                        print("User details not found")
                self.process_transaction(user_details)
                break
            else:
                print("Invalid OTP. Please try again.")
                continue

    def run(self):
        while True:
            self.display()
            choice = input("Enter The choice (1-3): ").strip()
            if choice == "1":
                self.process_signup()
            elif choice == "2":
                self.process_login()
            elif choice == "3":
                print("Thank you for using our system, Good Bye!")
                break
            else:
                print("Invalid Input please try again")
            input("Press Enter to continue...\n\n")
