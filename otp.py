import random

class OtpManager:

    def __init__(self):
        pass

    def generate_otp(self):
        return str(random.randint(1000,9999))