import re

class UserValidator:
    def __init__(self):
        self.email_pattern =   r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    def validate_email(self,email):
        return re.match(self.email_pattern,email) is not None

    def validate_phone(self,phone):
        phone = re.sub(r'[\s\-\(\)]', '', phone)
        return phone.isdigit() and 10 <= len(phone) <= 15