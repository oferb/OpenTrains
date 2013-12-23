from django.db import models
import json

# Create your models here.

class RawReport(models.Model):
    text = models.TextField()
    saved_at = models.DateTimeField(auto_now_add=True)
    def get_text_as_dict(self):
        return json.loads(self.text)
    def get_text_nice(self):
        return json.dumps(json.loads(self.text),indent=4)
    def to_json(self):
        return dict(text=self.text,saved_at=self.saved_at.isoformat(),id=self.id)


    
    
        

    
