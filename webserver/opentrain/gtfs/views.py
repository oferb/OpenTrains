from django.http import HttpResponse
import models
import utils
import json
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



