from config.celery import app
from django.core.mail import EmailMessage


@app.task
def send_email(code, to):
    email = EmailMessage("[Ctrlf] 이메일 인증코드가 도착 하였습니다!", f"커넵 이메일 인증 코드: {code}", to=[to])
    return email.send()
