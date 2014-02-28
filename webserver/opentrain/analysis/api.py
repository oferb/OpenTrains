from tastypie.resources import ModelResource,Resource,Bundle
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie import fields
import models
import logic

class SingleWifiResource(ModelResource):
    class Meta:
        queryset = models.SingleWifiReport.objects.all()
        
class LocationInfoResource(ModelResource):
    class Meta:
        queryset = models.LocationInfo.objects.all()

class ReportResource(ModelResource):
    wifis = fields.ToManyField(SingleWifiResource,'wifi_set',full=True)
    loc = fields.ToOneField(LocationInfoResource,'my_loc',full=True,null=True)
    class Meta:
        queryset = models.Report.objects.all().order_by('id').prefetch_related('wifi_set','my_loc')
        resource_name = "reports"
        ordering = 'id'
        filtering = {'device_id' : ALL,'id' : ALL_WITH_RELATIONS}
        
class ReportLocResource(ModelResource):
    loc = fields.ToOneField(LocationInfoResource,'my_loc',full=True,null=True)
    def dehydrate(self, bundle):
        bundle.data['is_station'] = bundle.obj.is_station()
        return bundle
    class Meta:
        queryset = models.Report.objects.order_by('id').filter(my_loc__isnull=False).prefetch_related('wifi_set','my_loc')
        resource_name = "reports-loc"
        ordering = 'id'
        filtering = {'device_id' : ALL, 'id' : ALL_WITH_RELATIONS}
                                
def register_all(tp):
    tp.register(ReportResource())
    tp.register(ReportLocResource())
    
    