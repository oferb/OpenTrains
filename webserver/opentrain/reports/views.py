from django.http.response import HttpResponseNotAllowed, HttpResponse

# Create your views here.

def add(req):
    if req.method != 'POST':
        return HttpResponseNotAllowed(permitted_methods=["POST"],content="405 - ONLY POST")
    print req.body
    
    return HttpResponse(status=201,content="report accepted")

