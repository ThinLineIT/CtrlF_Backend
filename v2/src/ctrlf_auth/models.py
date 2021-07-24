from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.core.mail import send_mail
from django.db import models


class CtrlfUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(email=self.normalize_email(email))

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(email, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class CtrlfUser(AbstractBaseUser):
    email = models.EmailField(verbose_name="email address", max_length=255, unique=True, help_text="email 주소")
    is_active = models.BooleanField(default=True, help_text="패스워드")
    nickname = models.CharField(max_length=30, help_text="닉네임")

    objects = CtrlfUserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class EmailAuthCode(models.Model):
    code = models.CharField(max_length=8, help_text="이메일 인증용 코드")

    def send_email(self, to):
        return send_mail(
            "[Ctrlf] 이메일 인증코드가 도착 하였습니다!", f"이메일 인증 코드: {self.code}", "noreplay@ctrlf.com", [to], fail_silently=False
        )
