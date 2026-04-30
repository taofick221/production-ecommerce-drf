from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    username=None
    email=models.CharField(unique=True)

    USERNAME_FIELD="email"
    REQUIRED_FIELDS=[]

    def __str__(self):
        return self.email
    

