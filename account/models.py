from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ("-created",)


class User(AbstractUser):
    username = models.CharField(unique=True)
    email = models.EmailField(null=True, blank=True)
    full_name = models.CharField(null=True, blank=True)
    is_account_verified = models.BooleanField(default=False)
    address = models.TextField()



class UserAccountActivationOTP(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_account_activation")
    otp = models.CharField(max_length=6)
    expires = models.DateTimeField()


