from django.contrib.auth.models import AbstractUser
from django.db import models

class Visita(models.Model):
    data = models.DateField(auto_now_add=True)
    contagem = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.data} - {self.contagem} visitas"

class CustomUser(AbstractUser):
    is_admin = models.BooleanField(default=False)
    primeiro_acesso = models.BooleanField(default=True)

    def __str__(self):
        return self.username

