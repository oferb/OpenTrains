from django.db import models

# Create your models here.

class WifiReport(models.Model):
    lat = models.CharField(max_length=20)
    lon = models.CharField(max_length=20)
    error_radius = models.FloatField()
    timestamp = models.FloatField()

class WifiFound(models.Model):
    report = models.ForeignKey(WifiReport)
    ssid = models.CharField(max_length=20)
    mac = models.CharField(max_length=20)
    power = models.IntegerField()
    channel = models.IntegerField()

class RawReport(models.Model):
    text = models.TextField()
    
        

    