from django.middleware.common import CommonMiddleware
import urlparse
import time
class OpenTrainMiddleware(CommonMiddleware):
    def process_response(self, request, response):
        from django.db import connection
        if hasattr(request,'prof_start_time'):
            request.prof_end_time = time.time()
            total_time = request.prof_end_time - request.prof_start_time
            print '%s %s Time = %.2f DB = %d' % (request.method,
                                                 urlparse.unquote(request.get_full_path()),
                                                 total_time,
                                                 len(connection.queries))
            
        if int(response.status_code) == 500:
            import tempfile
            t = tempfile.NamedTemporaryFile(delete=False,prefix="error_500_",suffix=".html")
            t.write(response.content)
            t.write("\n")
            t.close()
            print '*******************************************'
            print '** ERROR_500 Wrote to  file://%s' % t.name
            print '*******************************************'
 
        return response

    def process_request(self,request):
        request.prof_start_time = time.time()
        
        

    
    
