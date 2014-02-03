from django.middleware.common import CommonMiddleware
import re
from django.http.response import HttpResponse
API_RE = re.compile('/api/v1/trips/(\w+)/')

import ot_cache.models

class OpenTrainCacheMiddleware(CommonMiddleware):
    def process_response(self, request, response):
        cached_key = getattr(request,'cache_key',None)
        if cached_key:
            ot_cache.models.CacheJson(key=cached_key,value=response.content).save()
        return response
    
    def process_request(self,request):
        m = API_RE.match(request.path)
        if not m:
            return None
        key = m.group(1)    
        try:
            cached_resp = ot_cache.models.CacheJson.objects.get(key=key)
            print '[CACHE] %s from cache' % (key)
            return HttpResponse(content=cached_resp.value,content_type='application/json')
        except ot_cache.models.CacheJson.DoesNotExist:
            print '[CACHE] %s not in cache' % (key)
            request.cache_key = key
            return None
            
        
        
             
    
    