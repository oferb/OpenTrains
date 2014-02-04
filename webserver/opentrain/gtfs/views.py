from django.http import HttpResponse
import datetime
from django.http.response import HttpResponseNotAllowed,HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.views.generic import View
from django.core.urlresolvers import reverse

import models

import utils
import logic
import common.ot_utils
import json
 
@csrf_exempt
def create_all(req):
    if req.method == "POST":
        logic.create_all(download=False)
        return HttpResponse(status=201)
    return HttpResponseNotAllowed(permitted_methods=['GET'])

@csrf_exempt
def download_gtfs(req):
    if req.method == "POST":
        utils.download_gtfs_file()
        return HttpResponse(status=201)
    return HttpResponseNotAllowed(permitted_methods=['GET'])

@csrf_exempt
def create_superuser(req):
    from django.contrib.auth.models import User
    if req.method == 'POST':
        User.objects.create_superuser('root','hasadna.opentrain@gmail.com','opentrain')
        return HttpResponse(status=201)
    return HttpResponseNotAllowed(permitted_methods=['GET'])

def show_map(req,trip_id):
    ctx = dict()
    zoom_stop_id = req.GET.get('zoom_stop_id',0)
    if zoom_stop_id > 0:
        ctx['zoom_stop'] = models.Stop.objects.get(stop_id=zoom_stop_id)
    else:
        ctx['zoom_stop'] = None
    ctx['trip'] = models.Trip.objects.get(trip_id=trip_id)
    return render(req, 'gtfs/trip_map.html', ctx)

def home(req):
    return HttpResponse(content="hello and good day")

def gtfs_home(req):
    return HttpResponse("in gtfs")

class GtfsSearch(View):
    def get(self,req,*args,**kwargs):
        ctx = dict()
        initial = dict()
        defaultForm = dict(when=datetime.datetime.now(),before=30,after=30)
        for f in self.fields:
            value = req.GET.get(f,None)
            if value:
                if f == 'when':
                    initial[f] = common.ot_utils.parse_form_date(value)
                else:
                    initial[f] = value
                
        form = self.FormClass(initial=initial if initial else defaultForm)
        ctx['form'] = form        
        ctx['title'] = self.title
        ctx['url_name'] = self.url_name 
        if initial: 
            ctx['when'] = initial['when']
            ctx['results'] = logic.do_search(kind=self.url_name.split(':')[1],**initial) 
        return render(req, 'gtfs/search_form.html', ctx)
    
    def post(self,req,*args,**kwargs):
        import urllib
        form = self.FormClass(req.POST)
        if form.is_valid():
            params = dict()
            params.update(form.cleaned_data)
            params['when'] = req.POST['when']
            qs = urllib.urlencode(params)
            url = reverse(self.url_name)
            return HttpResponseRedirect('%s?%s' % (url,qs))
        raise Exception('Illegal Form')

class GtfsSearchBetween(GtfsSearch):
    import forms
    url_name = 'gtfs:search-between'
    fields = ['to_station','from_station','when','before','after']
    FormClass = forms.SearchBetweenForm
    title = 'Search Between'
    

class GtfsSearchIn(GtfsSearch):
    import forms
    url_name = 'gtfs:search-in'
    fields = ['in_station','when','before','after']
    FormClass = forms.SearchInForm
    title = 'Search In'

def get_trip_ids_for_date(request,*args,**kwargs):
    year = request.GET.get('year')
    month = request.GET.get('month')
    day = request.GET.get('day')
    if not year or not month or not day:
        raise Exception('year/month/day are mandatory')
    dt = datetime.date(year=int(year),month=int(month),day=int(day))
    trips = logic.get_all_trips_in_date(dt)
    trip_ids = [trip.trip_id for trip in trips] 
    return HttpResponse(status=200,content=json.dumps(trip_ids),content_type='application/json')
    
