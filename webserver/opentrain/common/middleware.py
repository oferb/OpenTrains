from django.middleware.common import CommonMiddleware
import urlparse
class OpenTrainMiddleware(CommonMiddleware):
    def process_response(self, request, response):
        from django.db import connection
        print '%s %s db DB = %d' % (request.method,urlparse.unquote(request.get_full_path()),len(connection.queries)) 
        return response
    
    
    
    