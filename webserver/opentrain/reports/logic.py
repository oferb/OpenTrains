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
    
def backup_reports(filename):
    chunk = 100
    index = 0
    import json
    
    with open(filename,'w') as fh:
        fh.write('[\n')
        is_first = True
        while True:
            reports = models.RawReport.objects.all()[index:index+chunk]
            reports_len = reports.count()
            if reports_len == 0:
                break
            for rr in reports:
                if not is_first:
                    fh.write(',')
                    fh.write('\n')
                else:
                    is_first = False
                fh.write(json.dumps(rr.to_json()))
            index += reports_len
        fh.write('\n]\n')
    print 'Backup %s reports to %s' % (index,filename)
            
    
        
        
    
    
    
    
    
    