from django.db import models

class Report(models.Model):
    device_id = models.CharField(max_length=50)
    timestamp = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return '%s @%s' % (self.device_id,self.timestamp)
    
    def is_station(self):
        """ this function returns using iteration and not using filter().exists()
        since it is called after prefetch_related, and using this style
        does not force acceess to the DB """
        for wifi in self.wifi_set.all():
            if wifi.SSID == 'S-ISRAEL-RAILWAYS':
                return True 
        return False
    
class LocationInfo(models.Model):
    report = models.OneToOneField(Report,related_name='my_loc')
    accuracy = models.FloatField()
    lat = models.FloatField()
    lon = models.FloatField()
    provider = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    
class SingleWifiReport(models.Model):
    report = models.ForeignKey(Report,related_name='wifi_set')
    SSID = models.CharField(max_length=50)
    frequency = models.FloatField()
    key = models.CharField(max_length=30)
    signal = models.IntegerField()
    def __unicode__(self):
        return self.SSID
    
class AnalysisMarker(models.Model):
    label = models.CharField(max_length=30)
    text = models.TextField()
    lat = models.CharField(max_length=10)
    lon = models.CharField(max_length=10)
    
    