from django.http import HttpResponse
import models
from django.http.response import HttpResponseNotAllowed,HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.views.generic import View

import utils
import ot_utils.ot_utils
from ot_global.ctx import get_global_context 

@csrf_exempt
@ot_utils.ot_utils.benchit
def create_all(req):
    if req.method == "POST":
        dirname = utils.find_gtfs_data_dir()
        cls_list = models.GTFSModel.__subclasses__()  # @UndefinedVariable
        for cls in cls_list: 
            cls.read_from_csv(dirname)
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

def home(req):
    return HttpResponse(content="hello and good day")

def gtfs_home(req):
    return HttpResponse("in gtfs")

class GtfsSearchBetween(View):
    def get(self,req,*args,**kwargs):
        import logic
        ctx = get_global_context('gtfs:search-between')
        ctx['stations'] = logic.get_stations()  
        from_id = req.GET.get('from_station',0)
        to_id = req.GET.get('to_station',0)
        ctx['from_id'] = int(from_id)
        ctx['to_id'] = int(to_id)
        
        return render(req, 'gtfs/search_between.html', ctx)
        
    def post(self,req,*args,**kwargs):
        import urllib
        params=dict(from_station=req.POST['from_station'],
                    to_station=req.POST['to_station'])
        qs = urllib.urlencode(params)
        return HttpResponseRedirect('/gtfs/search-between?%s' % (qs))

class GtfsSearchIn(View):
    def get(self,req,*args,**kwargs):
        import logic
        ctx = get_global_context('gtfs:search-in')
        ctx['stations'] = logic.get_stations()  
        in_id = req.GET.get('in_station',0)
        ctx['in_id'] = int(in_id) 
        return render(req, 'gtfs/search_in.html', ctx)
        
    def post(self,req,*args,**kwargs):
        import urllib
        params=dict(from_station=req.POST['in_station'])
        qs = urllib.urlencode(params)
        return HttpResponseRedirect('/gtfs/search-in?%s' % (qs))

