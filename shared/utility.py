from rest_framework.exceptions import ValidationError
import re

email_regex = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
phone_regex = re.compile(r"^\+?[1-9]\d{7,14}$")

def email_or_phone_number(value):
    # Email tekshirish
    if email_regex.fullmatch(value):
        return "email"

    # Phone tekshirish
    if phone_regex.fullmatch(value):
        return "phone_number"

    # Ikkalasi ham emas bo'lsa
    raise ValidationError("Invalid Email or Phone Number")
