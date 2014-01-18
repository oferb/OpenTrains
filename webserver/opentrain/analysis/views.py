import urllib
from django.shortcuts import render
import forms
import models
from django.views.generic.base import View
from django.http.response import HttpResponseRedirect

# Create your views here.

def show_labels(req):
    ctx = dict(form=forms.LabelsForm)
    return render(req,'analysis/show_labels.html',ctx)

class ShowReportDetails(View):
    def get(self,req):
        ctx = dict()
        f = forms.ReportDetailForm()
        report_id = req.GET.get('report_id',None) 
        if report_id:
            f.fields['report_id'].initial = report_id
            print report_id
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

class ShowDeviceReports(View):
    def get(self,req,*args,**kwargs):
        ctx = dict()
        if req.GET.get('device_desc'):
            device_desc = req.GET['device_desc']
            (device_id,device_date,device_count) = device_desc.split('::::')
            ctx['device_id'] = device_id
            ctx['device_date'] = device_date
            (device_date_year,device_date_month,device_date_day) = device_date.split(':')  # @UnusedVariable
            qs = models.Report.objects.filter(device_id=ctx['device_id'],my_loc__isnull=False)
            #qs = qs.filter(timestamp__day=device_date_day,timestamp__month=device_date_month,timestamp__year=device_date_year)
            qs = qs.order_by('timestamp')
            qs = qs.prefetch_related('wifi_set','my_loc')
            reports = list(qs)
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
        form = forms.ReportsForm(req.POST)
        if form.is_valid():
            device_desc = form.cleaned_data['device_desc']
            qs = urllib.urlencode(dict(device_desc=device_desc))
            return HttpResponseRedirect('%s?%s' % (req.path,qs))
        ctx = dict()
        ctx['form'] = form
        return render(req,'analysis/show_reports.html',ctx)



