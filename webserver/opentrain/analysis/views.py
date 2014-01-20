import urllib
import datetime
from django.shortcuts import render
import forms
import models
from django.views.generic.base import View
from django.http.response import HttpResponseRedirect, HttpResponse
import common.ot_utils

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
            start_time = req.GET.get('start_time',None)
            end_time = req.GET.get('end_time',None)
            filter_start_time = common.ot_utils.parse_form_date(start_time)
            filter_end_time = common.ot_utils.parse_form_date(end_time)
            try:
                (device_id,device_date) = device_desc.split('::::')
            except ValueError:
                return HttpResponse(status=400,content='Wrong query paramter')
            ctx['device_id'] = device_id
            ctx['device_date'] = device_date
            try:
                (device_date_year,device_date_month,device_date_day) = device_date.split(':')  # @UnusedVariable
            except ValueError:
                return HttpResponse(status=400,content='Wrong query paramter')
            qs = models.Report.objects.filter(device_id=ctx['device_id'],my_loc__isnull=False)
            global_reports_count = qs.count()
            global_first_report = qs.earliest('timestamp')
            global_last_report = qs.latest('timestamp')
            #qs = qs.filter(timestamp__day=device_date_day,timestamp__month=device_date_month,timestamp__year=device_date_year)
            if filter_start_time:
                qs = qs.filter(timestamp__gte=filter_start_time)
            if filter_end_time:
                qs = qs.filter(timestamp__lte=filter_end_time+datetime.timedelta(seconds=60))
            qs = qs.order_by('timestamp')
            reports_count = qs.count()
            if reports_count > 0:
                first_report = qs.earliest('timestamp')
                last_report = qs.latest('timestamp')
            else:
                first_report = None
                last_report = None
            qs = qs.prefetch_related('wifi_set','my_loc')
            reports = list(qs)
            ctx['filter_start_time'] = filter_start_time
            ctx['filter_end_time'] = filter_end_time
            ctx['reports'] =  reports
            ctx['no_loc_reports_count'] = models.Report.objects.filter(device_id=ctx['device_id'],my_loc__isnull=True).count()
            ctx['stop_points_count'] = sum(1 for r in reports if r.is_station())
            if reports:
                ctx['center'] = dict(lon=ctx['reports'][0].my_loc.lon,lat=ctx['reports'][0].my_loc.lat)
            if first_report:
                ctx['start_time'] = first_report.timestamp
                ctx['end_time'] = last_report.timestamp
            ctx['global_start_time'] = global_first_report.timestamp
            ctx['global_end_time'] = global_last_report.timestamp
            ctx['global_reports_count'] = global_reports_count
            
            f = forms.ReportsForm()
            f.fields['device_desc'].initial = device_desc
            form_first_time = None
            if first_report:
                form_first_time = first_report.timestamp
            elif filter_start_time:
                form_first_time = filter_start_time
                
            form_last_time = None
            if last_report:
                form_last_time = last_report.timestamp
            elif filter_end_time:
                form_last_time = filter_end_time
                
            f.fields['start_time'].initial = form_first_time  
            f.fields['end_time'].initial = form_last_time 
            ctx['form'] = f
            
        else:
            f = forms.ReportsForm()
            ctx['form'] = f 
            
        result = render(req,'analysis/show_reports.html',ctx)
        return result 
    
    def post(self,req,*args,**kwargs):
        form = forms.ReportsForm(req.POST)
        if form.is_valid():
            device_desc = form.cleaned_data['device_desc']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            qs = urllib.urlencode(dict(device_desc=device_desc,
                                       start_time=start_time,
                                       end_time=end_time))
            return HttpResponseRedirect('%s?%s' % (req.path,qs))
        ctx = dict()
        ctx['form'] = form
        return render(req,'analysis/show_reports.html',ctx)



