import urllib
from django.shortcuts import render
import forms
import models
from django.views.generic.base import View
from django.http.response import HttpResponseRedirect, HttpResponse
from django.conf import settings

class ShowReportDetails(View):
    def get(self,req):
        ctx = dict()
        f = forms.ReportDetailForm()
        report_id = req.GET.get('report_id',None) 
        if report_id:
            f.fields['report_id'].initial = report_id
            ctx['report'] = models.Report.objects.get(id=report_id)
        ctx['form'] = f    
        return render(req,'analysis/report_details.html',ctx)
    def post(self,req,*args,**kwargs):
        form = forms.ReportDetailForm(req.POST)
        if form.is_valid():
            report_id = form.cleaned_data['report_id']
            qs = urllib.urlencode(dict(report_id=report_id))
            return HttpResponseRedirect('%s?%s' % (req.path,qs))
        ctx = dict()
        ctx['form'] = form
        return render(req,'analysis/show_reports.html',ctx)

def show_device_reports(req):
    return render(req,'analysis/show_device_reports.html')

def show_live_trains(req):
    return render(req,'analysis/show_live_trains.html')
         
