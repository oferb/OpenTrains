from django.db import models
import json

# Create your models here.

class RawReport(models.Model):
    text = models.TextField()
    def get_text_as_dict(self):
        return json.loads(self.text)
    def get_text_nice(self):
         return json.dumps(json.loads(self.text),indent=4)
    
        

    
