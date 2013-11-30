from django.http import HttpResponse
import models
import utils
import json

def create_all(req):
    dirname = utils.find_gtfs_data_dir() 
    models.Agency.read_from_csv(dirname)
    content = json.dumps(get_all_models())
    return HttpResponse(status=200,
                        content_type='application/json',
                        content=content)


def get_all_models():
    all_models = []
    all_models.extend(models.Agency.objects.all())
    return [m.to_json() for m in all_models]
