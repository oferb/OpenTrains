from django.db import models
import csv
import os

class GTFSModel(models.Model):
    class Meta:
        abstract = True
    def read_from_csv(self,dir):
        full = os.path.join(dir,self.filename)
        with open(full) as fh:
            reader = csv.DictReader(fh, delimiter=',')
            for row in reader:
                for (key,value) in row.iteritems():
                    setattr(self,key.decode('utf-8-sig'),value.decode('utf-8-sig'))
            
class Agency(GTFSModel):
    filename = "agency.txt"
    agency_id = models.CharField(max_length=255)
    agency_name = models.TextField()
    agency_url = models.TextField()
    agency_timezone = models.TextField()
    agency_lang = models.CharField(max_length=20)
    

    