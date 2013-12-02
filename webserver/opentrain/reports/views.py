from django.http.response import HttpResponseNotAllowed, HttpResponse
from django.views.decorators.csrf import csrf_exempt

import json

# Create your views here.

@csrf_exempt
def add(req):
    if req.method != 'POST':
        return HttpResponseNotAllowed(permitted_methods=["POST"],content="405 - ONLY POST")
    body = req.body
    print json.dumps(json.loads(body),indent=4)
    
    return HttpResponse(status=201,content="report accepted")

