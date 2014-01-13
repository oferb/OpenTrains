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
        ctx = dict(form=forms.ReportsForm())
        return render(req,'analysis/show_reports.html',ctx) 
    
    def post(self,req,*args,**kwargs):
        import urllib
        form = forms.ReportsForm(req.POST)
        if form.is_valid():
            pair = form.cleaned_data['pair']
            device_id,timestamp = pair.split(' @')
            qs = urllib.urlencode(dict(timestamp=timestamp,device_id=device_id))
            url = reverse('analysis:show-device-reports')
            return HttpResponseRedirect('%s?%s' % (url,qs))
        raise Exception('Illegal Form')

def show_reports_on_map(req):
    ctx = dict()
    ctx['device_id'] = req.GET['device_id']
    ctx['timestamp'] = req.GET['timestamp']
    ctx['reports'] = list(models.Report.objects.filter(device_id=ctx['device_id'],my_loc__isnull=False)) # TODO - add timestamp
    ctx['no_loc_reports_count'] = models.Report.objects.filter(device_id=ctx['device_id'],my_loc__isnull=True).count()
    ctx['center'] = dict(lon=ctx['reports'][0].my_loc.lon,lat=ctx['reports'][0].my_loc.lat)
    return render(req,'analysis/analysis_map.html',ctx)        




