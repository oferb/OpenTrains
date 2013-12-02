from tastypie.resources import ModelResource
from tastypie import fields
import models

class RawReportResource(ModelResource):
    class Meta:
        queryset = models.RawReport.objects.all()
        resource_name = 'raw-reports'
        
def register_all(tp):
    tp.register(RawReportResource())
    
    
    