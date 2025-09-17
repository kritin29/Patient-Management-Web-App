import random

from flask_mail import Message

from dental_clinic import mail


def generate_otp():
    return ''.join(str(random.randint(1, 6)) for _ in range(5))


def send_otp_email(user, email, otp):
    otp_email = Message('Authenticate your email', sender="mutyamkritin.29@gmail.com", recipients=[email])
    otp_email.body = f"Hello {user},\n\nPlease use this OTP to authenticate your email: {otp}\n\nDo not share the OTP anywhere, also keep in mind that we do not call or message our clients to share the OTP with us.\n\n Warm Regards,\nDental Clinic"
    mail.send(otp_email)