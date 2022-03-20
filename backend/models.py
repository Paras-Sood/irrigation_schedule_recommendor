from django.db import models

from django.contrib.auth.models import AbstractUser

CROP_CHOICES=(
    ("rice","rice"),
    ("wheat","wheat")
)

class User(AbstractUser):
    pass

class Field(models.Model):
    owner=models.ForeignKey(User,on_delete=models.CASCADE,related_name="field")
    field_area=models.DecimalField(max_digits=7,decimal_places=2)

class Crop(models.Model):
    field=models.ForeignKey(Field,on_delete=models.CASCADE,related_name="crops")
    crop=models.CharField(max_length=10,choices=CROP_CHOICES)

class Data(models.Model):
    crop=models.ForeignKey(Crop,on_delete=models.CASCADE,related_name="data")
    date=models.DateField(auto_now_add=True)
    wateramount=models.DecimalField(max_digits=7,decimal_places=2)

class SampleSensorData(models.Model):
    temperature=models.DecimalField(max_digits=5,decimal_places=2)
    relative_humidity=models.DecimalField(max_digits=5,decimal_places=2)
    pressure=models.DecimalField(max_digits=6,decimal_places=2)
    wind_speed=models.DecimalField(max_digits=4,decimal_places=2)
    short_wave_irradiation=models.DecimalField(max_digits=7,decimal_places=4)
    soil_moisture=models.DecimalField(max_digits=5,decimal_places=2)