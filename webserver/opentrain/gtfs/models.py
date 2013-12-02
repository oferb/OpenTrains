from django.db import models
import csv
import os

class GTFSModel(models.Model):
    class Meta:
        abstract = True
    @classmethod
    def read_from_csv(cls,dirname):
        full = os.path.join(dirname,cls.filename)
        print('Reading from %s from class %s' % (full,cls.__name__))
        with open(full) as fh:
            reader = csv.DictReader(fh, delimiter=',')
            index = 0
            objs_to_save = []
            for row in reader:
                index+=1
                m = cls()
                fields = [f.name for f in cls._meta.fields]
                for (key,value) in row.iteritems():
                    key_decoded = key.decode('utf-8-sig')
                    value_decoded = value.decode('utf-8-sig')
                    is_field = False
                    if key_decoded in fields:
                        is_field = True
                    if not is_field and key_decoded.endswith('_id') and key_decoded[:-3] in fields:
                        is_field = True
                    if not is_field:
                        raise Exception('key %s is not a field of %s' % (key,cls.__name__))  
                    setattr(m,key_decoded,value_decoded)
                objs_to_save.append(m)
                if index % 10000 == 0:
                    cls.objects.bulk_create(objs_to_save)
                    print('%s: Saved %d rows so far' % (cls.__name__,index))
                    objs_to_save = []
            cls.objects.bulk_create(objs_to_save)
            print('%s: Saved %d rows so far' % (cls.__name__,index))
            objs_to_save = []
        
            
                    
    def to_json(self):
        result = dict()
        for f in self.__class__._meta.fields:
            result[f.name] = getattr(self,f.name)
        return result
            
class Agency(GTFSModel):
    filename = "agency.txt"
    agency_id = models.IntegerField(primary_key=True,default=1,max_length=255)
    agency_name = models.TextField()
    agency_url = models.TextField()
    agency_timezone = models.TextField()
    agency_lang = models.CharField(max_length=20)
      
class Route(GTFSModel):
    filename = "routes.txt"
    route_id = models.IntegerField(primary_key=True)
    agency_id = models.ForeignKey('Agency',default=1)
    route_short_name = models.CharField(max_length=255)
    route_long_name = models.CharField(max_length=255)
    route_desc = models.TextField()
    route_type = models.IntegerField()
    route_color = models.CharField(max_length=10)
    route_text_color = models.CharField(max_length=20)
    
class Trip(GTFSModel):
    filename = "trips.txt"
    route = models.ForeignKey('Route')
    service = models.ForeignKey('Service')
    trip_id = models.CharField(max_length=100,primary_key=True)
    direction_id = models.IntegerField()
    shape_id = models.CharField(max_length=100)
    wheelchair_accessible = models.IntegerField()
    trip_headsign = models.CharField(max_length=100)
    
    
class Service(GTFSModel):
    filename = "calendar.txt"
    service_id = models.CharField(max_length=100,primary_key=True)
    monday = models.BooleanField()
    tuesday = models.BooleanField()
    wednesday = models.BooleanField()
    thursday = models.BooleanField()
    friday = models.BooleanField()
    saturday = models.BooleanField()
    sunday = models.BooleanField()
    start_date = models.CharField(max_length=100)
    end_date = models.CharField(max_length=100)
    
class StopTime(GTFSModel):
    filename = "stop_times.txt"
    trip = models.ForeignKey('Trip')
    arrival_time = models.CharField(max_length=20)
    departure_time = models.CharField(max_length=20)
    stop = models.ForeignKey('Stop')
    stop_sequence = models.IntegerField()
    
class Stop(GTFSModel):
    filename = "stops.txt"
    stop_id = models.IntegerField(primary_key=True)
    stop_name = models.CharField(max_length=200)
    stop_lat = models.CharField(max_length=20)
    stop_lon = models.CharField(max_length=20)
    stop_url = models.URLField()
    location_type = models.IntegerField()
    
    
class Shape(GTFSModel):
    filename = "shapes.txt"
    shape_id = models.CharField(max_length=100)
    shape_pt_lat = models.CharField(max_length=20)
    shape_pt_lon = models.CharField(max_length=20)
    shape_pt_sequence = models.IntegerField()
    
    