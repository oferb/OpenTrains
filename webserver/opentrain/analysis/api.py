from tastypie.resources import ModelResource,Resource,Bundle
from tastypie.constants import ALL, ALL_WITH_RELATIONS
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
    loc = fields.ToOneField(LocationInfoResource,'my_loc',full=True,null=True)
    class Meta:
        queryset = models.Report.objects.all().prefetch_related('wifi_set','my_loc')
        resource_name = "reports"
        ordering = 'id'
        filtering = {'device_id' : ALL}
        
class ReportLocResource(ModelResource):
    loc = fields.ToOneField(LocationInfoResource,'my_loc',full=True,null=True)
    def dehydrate(self, bundle):
        bundle.data['is_station'] = bundle.obj.is_station()
        return bundle
    class Meta:
        queryset = models.Report.objects.all().prefetch_related('wifi_set','my_loc')
        resource_name = "reports-loc"
        ordering = 'id'
        filtering = {'device_id' : ALL}

def get_devices_summary():
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("""
        SELECT device_id,MIN(DATE(timestamp)) as device_date,
        COUNT(*) from analysis_report 
        GROUP BY device_id 
        ORDER BY device_date
    """)
    tuples = cursor.fetchall()
    result = []
    for t in tuples:
        d = DeviceObject(device_id=t[0],
                         device_date=t[1],
                         device_count=t[2])
        result.append(d)
    return result

class DeviceObject(object):
    def __init__(self,device_id=None,device_date=None,device_count=None):
        self.device_id = device_id
        self.device_date = device_date
        self.device_count = device_count

class DeviceResource(Resource):
    device_id = fields.CharField(attribute='device_id')
    device_date = fields.DateTimeField(attribute='device_date')
    device_count = fields.IntegerField(attribute='device_count')
    
    class Meta:
        resource_name = 'devices'
        object_class = DeviceObject
    
    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}

        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.device_id
        else:
            kwargs['pk'] = bundle_or_obj.device_id

        return kwargs

    def get_object_list(self, request):
        return get_devices_summary()

    def obj_get_list(self, bundle, **kwargs):
        # Filtering disabled for brevity...
        return self.get_object_list(bundle.request)

    def obj_get(self, bundle, **kwargs):
        objects = self.get_object_list(bundle.request)
        for obj in objects:
            if obj.device_id == kwargs['pk']:
                return obj
            
        
def register_all(tp):
    tp.register(ReportResource())
    tp.register(ReportLocResource())
    tp.register(DeviceResource())
    
    