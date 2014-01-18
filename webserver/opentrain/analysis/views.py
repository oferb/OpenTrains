from django.shortcuts import render
import forms
from django.views.generic.base import View
from django.http.response import HttpResponseRedirect
from django.core.urlresolvers import reverse
import models
# Create your views here.

def show_labels(req):
    ctx = dict(form=forms.LabelsForm)
    return render(req,'analysis/show_labels.html',ctx)


class ShowDeviceReports(View):
    def get(self,req,*args,**kwargs):
        ctx = dict()
        if req.GET.get('device_desc'):
            device_desc = req.GET['device_desc']
            (device_id,device_date,device_count) = device_desc.split('::::')
            ctx['device_id'] = device_id
            ctx['device_date'] = device_date
            reports = list(models.Report.objects.filter(device_id=ctx['device_id'],my_loc__isnull=False).prefetch_related('wifi_set','my_loc').order_by('timestamp'))
            ctx['reports'] =  reports
            ctx['no_loc_reports_count'] = models.Report.objects.filter(device_id=ctx['device_id'],my_loc__isnull=True).count()
            ctx['stop_points_count'] = sum(1 for r in reports if r.is_station())
            ctx['center'] = dict(lon=ctx['reports'][0].my_loc.lon,lat=ctx['reports'][0].my_loc.lat)
            ctx['start_time'] = ctx['reports'][0].timestamp
            ctx['end_time'] = ctx['reports'][-1].timestamp
            f = forms.ReportsForm()
            f.fields['device_desc'].initial = device_desc
            ctx['form'] = f
        else:
            ctx['form'] = forms.ReportsForm()
        result = render(req,'analysis/show_reports.html',ctx)
        return result 
    
    def post(self,req,*args,**kwargs):
        import urllib
        form = forms.ReportsForm(req.POST)
        if form.is_valid():
            device_desc = form.cleaned_data['device_desc']
            qs = urllib.urlencode(dict(device_desc=device_desc))
            url = reverse('analysis:select-device-reports')
            return HttpResponseRedirect('%s?%s' % (url,qs))
        raise Exception('Illegal Form')



