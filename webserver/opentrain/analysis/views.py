from django.shortcuts import render
import forms
from django.views.generic.base import View
from django.http.response import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
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
            params=dict(timestamp=form.cleaned_data['timestamp'],
                        device_id=form.cleaned_data['device_id']
                        )
            qs = urllib.urlencode(params)
            url = reverse('analysis:show-device-reports')
            return HttpResponseRedirect('%s?%s' % (url,qs))
        raise Exception('Illegal Form')

def show_reports_on_map(req):
    return HttpResponse('not yet')        




