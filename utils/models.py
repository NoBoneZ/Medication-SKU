from django.db import models

from account.models import BaseModel


# Create your models here.


class ErrorLog(BaseModel):
    title = models.CharField(max_length=500)
    error = models.TextField(null=True, blank=True)
    request = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title