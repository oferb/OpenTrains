from django.http.response import HttpResponseNotAllowed, HttpResponse,\
    HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import models
import json

# Create your views here.
MAX_REPORTS = 10
@csrf_exempt
def add(req):
    if req.method != 'POST':
        return HttpResponseNotAllowed(permitted_methods=["POST"],content="405 - ONLY POST")
    
    body = req.body
    text = json.dumps(json.loads(body))
    rep = models.RawReport(text=text)
    rep.save()
    #count = models.RawReport.objects.all().count()
    #if count > MAX_REPORTS:
    #    r = models.RawReport.objects.all().order_by('id')[count-MAX_REPORTS]
    #    models.RawReport.objects.filter(id__lt=r.id).delete()
    
    return HttpResponse(status=201,content="report accepted")

def show(req):
    rrs = list(models.RawReport.objects.order_by('-id'))
    data = dict(rrs=rrs)
    return render(req,'reports/results.html',data)

    
