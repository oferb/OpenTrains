from django.db import models

class WifiReport(models.Model):
    device_id = models.CharField(max_length=50)
    timestamp = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)

class WifiInReport(models.Model):
    report = models.ForeignKey(WifiReport,related_name='wifi_set')
    SSID = models.CharField(max_length=20)
    frequency = models.FloatField()
    key = models.CharField(max_length=20)
    signal = models.IntegerField()
    
    
