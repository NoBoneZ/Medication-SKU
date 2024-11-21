from datetime import timedelta

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.timezone import now

from account.models import UserAccountActivationOTP
from utils.helper_functions import generate_random_characters


def send_otp_for_verification(user_id: str, email: str):
    UserAccountActivationOTP.objects.only("id").filter(user_id=user_id).delete()
    otp = generate_random_characters(length=6)
    UserAccountActivationOTP.objects.create(
        user_id=user_id,
        otp=otp,
        expires=now() + timedelta(minutes=5)
    )

    receiver = (email,)
    msg_html = render_to_string('emails/otp_email.html', dict(otp_code=otp))
    msg = EmailMessage(subject="Your One-Time Password (OTP) for Account Verification", body=otp, from_email=settings.EMAIL_HOST_USER, to=receiver)
    msg.content_subtype = "html"
    msg.send()
    return "Done"