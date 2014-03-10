from django.shortcuts import render
from django.http.response import HttpResponse
import json

def get_config(request):
    import config
    return HttpResponse(status=200,content_type='application/json',content=json.dumps(config.get_client_config()))

