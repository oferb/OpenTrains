import models
import json
import reports.models

def analyze_raw_reports():
    items = collect_all_items()
    for (idx,item) in enumerate(items):
        if idx % 100 == 0:
            print '%d/%d' % (idx,len(items))
        if 'wifi' in item.keys():
            m = models.WifiReport(device_id=item['device_id'],timestamp=item['time'])
            m.save()
            for wifi in item['wifi']:
                w = models.WifiInReport(SSID=wifi['SSID'],
                                 signal=wifi['signal'],
                                 frequency=wifi['frequency'],
                                 key=wifi['key'])
                m.wifi_set.add(w)

    
def delete_all_reports():
    delete_from_model(models.WifiInReport)
    delete_from_model(models.WifiReport)
    
def delete_from_model(model):
    from django.db import connection
    cursor = connection.cursor()
    table_name = model._meta.db_table 
    sql = "DELETE FROM %s;" % (table_name, )
    cursor.execute(sql)    
    print 'DELETED %s' % (table_name)
def collect_all_items():
    delete_all_reports()
    all_reports = reports.models.RawReport.objects.all()
    result = []
    for rj in all_reports:
        items = json.loads(rj.text)['items']
        result.extend(items)
    return result








    
        