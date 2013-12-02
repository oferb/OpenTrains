from django.http.response import HttpResponseNotAllowed, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import models
import json

# Create your views here.
MAX_REPORTS = 10
@csrf_exempt
def add(req):
    if req.method != 'POST':
        return HttpResponseNotAllowed(permitted_methods=["POST"],content="405 - ONLY POST")
    try:
        body = req.body
        text = json.dumps(json.loads(body))
        rep = models.RawReport(text=text)
        rep.save()
        count = models.RawReport.objects.all().count()
        if count > MAX_REPORTS:
            r = models.RawReport.objects.all().order_by('id')[count-MAX_REPORTS]
            models.RawReport.objects.filter(id__lt=r.id).delete()
    except Exception,e:
        print e
        raise e
    
    return HttpResponse(status=201,content="report accepted")

