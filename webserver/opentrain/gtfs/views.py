from django.http import HttpResponse
import models
import utils
from django.http.response import HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def create_all(req):
    if req.method == "POST":
        dirname = utils.find_gtfs_data_dir()
        cls_list = models.GTFSModel.__subclasses__()  # @UndefinedVariable
        for cls in cls_list: 
            cls.read_from_csv(dirname)
        return HttpResponse(status=201)
    return HttpResponseNotAllowed()

@csrf_exempt
def download_gtfs(req):
    if req.method == "POST":
        utils.download_gtfs_file()
        return HttpResponse(status=201)
    return HttpResponseNotAllowed()

@csrf_exempt
def create_superuser(req):
    from django.contrib.auth.models import User
    if req.method == 'POST':
        User.objects.create_superuser('root','hasadna.opentrain@gmail.com','opentrain')
        return HttpResponse(status=201)
    return HttpResponseNotAllowed()

