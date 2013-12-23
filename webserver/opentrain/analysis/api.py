from tastypie.resources import ModelResource
from tastypie import fields
import models

class SingleWifiResource(ModelResource):
    class Meta:
        queryset = models.SingleWifiReport.objects.all()
        
class LocationInfoResource(ModelResource):
    class Meta:
        queryset = models.LocationInfo.objects.all()

class ReportResource(ModelResource):
    wifis = fields.ToManyField(SingleWifiResource,'wifi_set',full=True)
    loc = fields.ToOneField(LocationInfoResource,'my_loc',full=True)
    class Meta:
        queryset = models.Report.objects.all()
        resource_name = "reports"
        ordering = 'id'

        
def register_all(tp):
    tp.register(ReportResource())
    
    