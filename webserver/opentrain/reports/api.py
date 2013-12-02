from tastypie.resources import ModelResource
from tastypie import fields
import models

class RawReportResource(ModelResource):
    text = fields.DictField(models.RawReport.get_text_as_dict)
    class Meta:
        queryset = models.RawReport.objects.all()
        resource_name = 'raw-reports'
        fields = []
        
def register_all(tp):
    tp.register(RawReportResource())
    
    
    