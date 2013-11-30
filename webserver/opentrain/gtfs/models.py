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
                for (key,value) in row.iteritems():
                    setattr(m,key.decode('utf-8-sig'),value.decode('utf-8-sig'))
                objs_to_save.append(m)
                if index % 1000 == 0:
                    cls.objects.bulk_create(objs_to_save)
                    print('Saved %d rows so far' % (index))
                    objs_to_save = []
            cls.objects.bulk_create(objs_to_save)
            print('Saved %d rows so far' % (index))
            objs_to_save = []
        
            
                    
    def to_json(self):
        result = dict()
        for f in self.__class__._meta.fields:
            result[f.name] = getattr(self,f.name)
        return result
            
class Agency(GTFSModel):
    filename = "agency.txt"
    agency_id = models.CharField(max_length=255)
    agency_name = models.TextField()
    agency_url = models.TextField()
    agency_timezone = models.TextField()
    agency_lang = models.CharField(max_length=20)
      
class Route(GTFSModel):
    filename = "routes.txt"
    route_id = models.CharField(max_length=255)
    agency_id = models.CharField(max_length=255)
    route_short_name = models.CharField(max_length=255)
    route_long_name = models.CharField(max_length=255)
    route_desc = models.TextField()
    route_type = models.IntegerField()
    route_color = models.CharField(max_length=10)
    
class Trip(GTFSModel):
    filename = "trips.txt"
    route_id = models.CharField(max_length=255) # Route.route_id
    service_id = models.CharField(max_length=255) # Calendar.service_id
    trip_id = models.CharField(max_length=255) # stop_times
    direction_id = models.IntegerField()
    shape_id = models.CharField(max_length=255)
    

    