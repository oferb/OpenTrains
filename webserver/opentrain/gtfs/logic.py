import models

def get_stations():
    result = models.Stop.objects.all().order_by('stop_name')
    return list(result)



