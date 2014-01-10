from django.http.response import HttpResponseNotAllowed, HttpResponse
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
    count = int(req.GET.get('count',20))
    rrs = list(models.RawReport.objects.order_by('-id'))[0:count-1]
    total = models.RawReport.objects.count()
    data = dict(rrs=rrs,total=total)
    return render(req,'reports/results.html',data)

def download(req,count=-1):
    if count > 0:
        rrs = reversed(models.RawReport.objects.order_by('-id')[0:count])
    else:
        rrs = models.RawReport.objects.all()
    objects = []
    for rr in rrs:
        objects.append(rr.to_json())
    resp = HttpResponse(content=json.dumps(objects),content_type='application/json')
    return resp


