from django.db import models

class CacheJson(models.Model):
    key = models.CharField(db_index=True,max_length=100)
    value = models.TextField()

