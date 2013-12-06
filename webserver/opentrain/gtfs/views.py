from django.http import HttpResponse
import models
from django.http.response import HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

import utils
import ot_utils.ot_utils


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

def gtfs_search(req):
    import logic
    ctx = dict()
    ctx['stations'] = logic.get_stations() 
    return render(req, 'gtfs/search.html', ctx)
            

