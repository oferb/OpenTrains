from google.appengine.ext import db
import json

class RawReport(db.Model):
    timestamp = db.DateTimeProperty(auto_now=True)
    text = db.StringProperty()
    def get_text_nice(self):
        return json.dumps(json.loads(self.text),indent=4).replace(' ','&nbsp;').replace('\n','<br/>')
    



    
    
    
