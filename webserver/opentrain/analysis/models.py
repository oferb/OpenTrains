from django.db import models

class Report(models.Model):
    device_id = models.CharField(max_length=50)
    timestamp = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    
class LocationInfo(models.Model):
    report = models.ForeignKey(Report,related_name='my_loc')
    accuracy = models.FloatField()
    lat = models.FloatField()
    lng = models.FloatField()
    provider = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    
class SingleWifiReport(models.Model):
    report = models.ForeignKey(Report,related_name='wifi_set')
    SSID = models.CharField(max_length=20)
    frequency = models.FloatField()
    key = models.CharField(max_length=20)
    signal = models.IntegerField()
    
    
