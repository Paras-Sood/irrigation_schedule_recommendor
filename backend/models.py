from django.db import models

from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

class Data(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="data")
    field_area=models.DecimalField(max_digits=7,decimal_places=2)
    date=models.DateField(auto_now_add=True)
    