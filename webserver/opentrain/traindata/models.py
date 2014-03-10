from django.db import models

class TrainData(models.Model):
    date = models.DateField(db_index=True)
    train_num = models.IntegerField(db_index=True)
    exp_arrival = models.IntegerField()
    actual_arrival = models.IntegerField()
    exp_departure = models.IntegerField()
    actual_departure = models.IntegerField()
    raw_stop_id = models.IntegerField()
    raw_stop_name = models.CharField(max_length=30)
    stop = models.ForeignKey('gtfs.Stop',blank=True,null=True)
    file = models.CharField(max_length=30)
    line = models.IntegerField()
    #class Meta:
    #    unique_together = (('date','train_num','stop_id'))
    
    
    def __unicode__(self):
        return '%s %s %s %s' % (self.date,self.exp_arrival,self.train_num,self.stop_id)
        
        