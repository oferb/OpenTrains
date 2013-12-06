from django.http import HttpResponse
import models
from django.http.response import HttpResponseNotAllowed,HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.views.generic import View
from django.core.urlresolvers import reverse

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

class GtfsSearch(View):
    def get(self,req,*args,**kwargs):
        ctx = get_global_context('%s' % (self.url_name))
        initial = dict()
        for f in self.fields:
            value = req.GET.get(f,None)
            if value:
                if f == 'when':
                    initial[f] = ot_utils.ot_utils.parse_dt(value)
                else:
                    initial[f] = value
        form = self.FormClass(initial=initial)
        ctx['form'] = form        
        return render(req, self.template_name, ctx)
    
    def post(self,req,*args,**kwargs):
        import urllib
        form = self.FormClass(req.POST)
        #if form.is_valid():
        params = dict()
        for f in self.fields:
            params[f] = req.POST[f]
        qs = urllib.urlencode(params)
        url = reverse(self.url_name)
        return HttpResponseRedirect('%s?%s' % (url,qs))

class GtfsSearchBetween(GtfsSearch):
    import forms
    url_name = 'gtfs:search-between'
    template_name = 'gtfs/search_between.html'
    fields = ['to_station','from_station','when']
    FormClass = forms.SearchBetweenForm
    

class GtfsSearchIn(GtfsSearch):
    import forms
    url_name = 'gtfs:search-in'
    template_name = 'gtfs/search_in.html'
    fields = ['in_station','when']
    FormClass = forms.SearchInForm

