import models
import common.ot_utils
import json
import gzip

def restore_reports(filename,clean=True):
    """ restore reports from main server and restore them in
    local server - cleans first """
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
    
    if not filename.endswith('.gz'):
        raise Exception('filename must be gz file')
    
    with gzip.open(filename,'w') as fh:
        while True:
            reports = models.RawReport.objects.all().order_by('id')[index:index+chunk]
            reports_len = reports.count()
            if reports_len == 0:
                break
            for rr in reports:
                fh.write(json.dumps(rr.to_json()))
                fh.write("\n")
            index += reports_len
    print 'Backup %s reports to %s' % (index,filename)
            

def copy_device_reports(device_id,filename):
    chunk = 100
    index = 0
    wrote_count = 0
    
    with open(filename,'w') as fh:
        while True:
            reports = models.RawReport.objects.filter().order_by('id')[index:index+chunk]
            reports_len = reports.count()
            if reports_len == 0:
                break
            for rr in reports:
                rr_body = json.loads(rr.text)
                if rr_body['items'][0]['device_id'] == device_id:
                    fh.write(rr.text)
                    fh.write('\n')
                    wrote_count += len(rr_body['items'])
            index += reports_len
    print 'Wrote %s reports of device_id %s to %s' % (wrote_count,device_id,filename)
    
        
        
    
    
    
    
    
    