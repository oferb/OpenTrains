from django.db import models

class TrainData(models.Model):
    date = models.DateField()
    train_num = models.IntegerField()
    