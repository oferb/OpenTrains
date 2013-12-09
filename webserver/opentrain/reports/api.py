from tastypie.resources import ModelResource
from tastypie import fields
import models
import json

class RawReportResource(ModelResource):
    def dehydrate(self, bundle):
        bundle.data['text'] = json.loads(bundle.obj.text)
        return bundle
    class Meta:
        queryset = models.RawReport.objects.all()
        resource_name = 'raw-reports'
        ordering = 'id'
        
def register_all(tp):
    tp.register(RawReportResource())
    
    
    