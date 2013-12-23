import models
import common.ot_utils
import requests

MAIN_SERVER = '54.221.246.54'

def download_reports(clean=True):
    """ download reports from main server and restore them in
    local server - cleans first """
    if clean:
        print 'Deleting current raw reports'
        common.ot_utils.delete_from_model(models.RawReport)
    print 'Downloading json from %s' % (MAIN_SERVER)
    items = requests.get('http://%s/reports/download/' % (MAIN_SERVER)).json()
    print 'Downloaded %s items' % (len(items))
    print 'Start to add to DB'
    rrs = []
    for item in items:
        rr = models.RawReport(text=item['text'])
        rrs.append(rr)
    models.RawReport.objects.bulk_create(rrs)
    print 'Saved to DB. # of items in DB = %s' % (models.RawReport.objects.count())
    
    
        
        
    
    
    
    
    
    