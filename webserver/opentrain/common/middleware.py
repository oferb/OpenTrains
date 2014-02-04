from django.middleware.common import CommonMiddleware
import urlparse
import time
class OpenTrainMiddleware(CommonMiddleware):
    def process_response(self, request, response):
        from django.db import connection
        request.prof_end_time = time.time()
        total_time = request.prof_end_time - request.prof_start_time
        print '%s %s Time = %.2f DB = %d' % (request.method,
                                             urlparse.unquote(request.get_full_path()),
                                             total_time,
                                             len(connection.queries)) 
        return response
    
    def process_request(self,request):
        request.prof_start_time = time.time()
    
    