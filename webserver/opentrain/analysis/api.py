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


class DeviceResource(Resource):
    device_id = fields.CharField(attribute='device_id')
    device_date = fields.DateTimeField(attribute='device_date')
    device_count = fields.IntegerField(attribute='device_count')
    
    class Meta:
        resource_name = 'devices'
        object_class = logic.DeviceObject
    
    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}

        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.device_id
        else:
            kwargs['pk'] = bundle_or_obj.device_id

        return kwargs

    def get_object_list(self, request):
        return logic.get_devices_summary()

    def obj_get_list(self, bundle, **kwargs):
        # Filtering disabled for brevity...
        return self.get_object_list(bundle.request)

    def obj_get(self, bundle, **kwargs):
        objects = self.get_object_list(bundle.request)
        for obj in objects:
            if obj.device_id == kwargs['pk']:
                return obj
            
        
            
class TripLocationResource(Resource):
    trip_id = fields.CharField(attribute='trip_id')
    cur_point = fields.DictField(attribute='get_cur_point')
    exp_point = fields.DictField(attribute='get_exp_point')
    timestamp = fields.DateTimeField(attribute='timestamp')
    
    class Meta:
        resource_name = 'live-trips'
        object_class = logic.TripLocationObject

    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}

        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.trip_id
        else:
            kwargs['pk'] = bundle_or_obj.trip_id

        return kwargs

    def get_object_list(self, request):
        return logic.get_current_trips()

    def obj_get_list(self, bundle, **kwargs):
        # Filtering disabled for brevity...
        return self.get_object_list(bundle.request)

    def obj_get(self, bundle, **kwargs):
        objects = self.get_object_list(bundle.request)
        for obj in objects:
            if obj.trip_id == kwargs['pk']:
                return obj
            
                        
def register_all(tp):
    tp.register(ReportResource())
    tp.register(ReportLocResource())
    tp.register(DeviceResource())
    tp.register(TripLocationResource())
    
    