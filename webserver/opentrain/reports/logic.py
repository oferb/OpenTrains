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
    items = requests.get('http://%s/reports/download/' % (MAIN_SERVER),params=dict(count=50,offset=0)).json()
    print 'Downloaded %s items' % (len(items))
    print 'Start to add to DB'
    rrs = []
    for item in items:
        rr = models.RawReport(text=item['text'])
        rrs.append(rr)
    models.RawReport.objects.bulk_create(rrs)
    print 'Saved to DB. # of items in DB = %s' % (models.RawReport.objects.count())


def restore_reports(filename,clean=True):
    """ restore reports from main server and restore them in
    local server - cleans first """
    import gzip
    import json
    if not filename.endswith('gz'):
        raise Exception('%s must be gz file' % (filename))
    if clean:
        print 'Deleting current raw reports'
        common.ot_utils.delete_from_model(models.RawReport)
    rrs = []
    with gzip.open(filename,'r') as fh:
        for line in fh:
            item = json.loads(line)
            rr = models.RawReport(text=item['text'])
            rrs.append(rr)
    print 'Read %d raw reports from %s- saving to DB' % (len(rrs),filename)
    models.RawReport.objects.bulk_create(rrs)
    print 'Saved to DB. # of items in DB = %s' % (models.RawReport.objects.count())

    
def backup_reports(filename):
    chunk = 100
    index = 0
    import json
    import gzip
    
    if not filename.endswith('.gz'):
        raise Exception('filename must be gz file')
    
    with gzip.open(filename,'w') as fh:
        while True:
            reports = models.RawReport.objects.all()[index:index+chunk]
            reports_len = reports.count()
            if reports_len == 0:
                break
            for rr in reports:
                fh.write(json.dumps(rr.to_json()))
                fh.write("\n")
            index += reports_len
    print 'Backup %s reports to %s' % (index,filename)
            
    
        
        
    
    
    
    
    
    