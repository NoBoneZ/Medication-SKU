from random import sample
from re import search
from string import punctuation, digits, ascii_lowercase, ascii_uppercase

from django.contrib.auth.password_validation import validate_password

from utils.models import ErrorLog


def password_validator(password: str) -> bool:
    pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$'
    return search(pattern, password) is not None


def compound_password_validator(password: str) -> tuple:
    try:
        validate_password(password)
    except Exception as e:
        return False, "".join(e)

    if not password_validator(password):
        return False, ("Password needs to be more than 7 characters long and contain a digit, a symbol, an uppercase "
                       "letter and a lowercase letter !")

    return True, ""



def log_error(title: str, error: str, request: str = ""):
    ErrorLog.objects.create(title=title, error=error, request=request)


def generate_random_characters(length: int = 10, is_mixture: bool = False):
    if is_mixture:
        combo = digits + punctuation + ascii_uppercase + ascii_lowercase
        return "".join(sample(list(combo), length))
    return "".join(sample(list(digits), length))