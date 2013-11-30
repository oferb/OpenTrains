from django.db import models
import csv
import os

class GTFSModel(models.Model):
    class Meta:
        abstract = True
    @classmethod
    def read_from_csv(cls,dirname):
        full = os.path.join(dirname,cls.filename)
        with open(full) as fh:
            reader = csv.DictReader(fh, delimiter=',')
            for row in reader:
                m = cls()
                for (key,value) in row.iteritems():
                    setattr(m,key.decode('utf-8-sig'),value.decode('utf-8-sig'))
                m.save()
                    
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
    

    