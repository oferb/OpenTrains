from django.db import models
import datetime 

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
    
    def loc_ts_delta(self):
        if self.my_loc:
            return (self.timestamp - self.my_loc.timestamp).total_seconds()
    
    def get_timestamp_israel_time(self):
        #local_time_delta = datetime.timedelta(0,2*3600)
        #return self.timestamp + local_time_delta
	from common.ot_utils import get_localtime
	return get_localtime(self.timestamp)
    
class LocationInfo(models.Model):
    report = models.OneToOneField(Report,related_name='my_loc')
    accuracy = models.FloatField()
    lat = models.FloatField()
    lon = models.FloatField()
    provider = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    
    @property
    def accuracy_in_coords(self):
        from common.ot_utils import meter_distance_to_coord_distance
        return meter_distance_to_coord_distance(self.accuracy)
    
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
    
    
