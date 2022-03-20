from django.contrib import admin

from backend.models import User,Field,Crop,SampleSensorData

admin.site.register(User)
admin.site.register(Field)
admin.site.register(Crop)
admin.site.register(SampleSensorData)
