import models
import json
import reports.models
import common.ot_utils

def analyze_raw_reports(clean=True):
    if clean:
        delete_all_reports()
    items = _collect_all_items()
    wifis = []
    locs = []
    for (idx,item) in enumerate(items):
        if idx % 100 == 0:
            print '%d/%d' % (idx,len(items))
        if 'wifi' in item.keys():
            report_dt = common.ot_utils.get_utc_time_from_timestamp(float(item['time'])/1000)
            m = models.Report(device_id=item['device_id'],timestamp=report_dt)
            m.save()
            item_loc = item.get('location_api')
            if item_loc:
                loc = models.LocationInfo(report=m,
                                          lat=item_loc['lat'],
                                          lng=item_loc['long'],
                                          provider=item_loc['provider'],
                                          timestamp = common.ot_utils.get_utc_time_from_timestamp(float(item_loc['time'])/1000),
                                          accuracy = item_loc['accuracy'])
                locs.append(loc)
            for wifi in item['wifi']:
                wifis.append(models.SingleWifiReport(SSID=wifi['SSID'],
                                 signal=wifi['signal'],
                                 frequency=wifi['frequency'],
                                 key=wifi['key'],
                                 report=m))
    print 'Saving all dependant objects'
    models.SingleWifiReport.objects.bulk_create(wifis)
    models.LocationInfo.objects.bulk_create(locs)
    
    


def delete_all_reports():
    common.ot_utils.delete_from_model(models.SingleWifiReport)
    common.ot_utils.delete_from_model(models.LocationInfo)
    common.ot_utils.delete_from_model(models.Report)
    
def _collect_all_items():
    all_reports = reports.models.RawReport.objects.all()
    result = []
    for rj in all_reports:
        items = json.loads(rj.text)['items']
        result.extend(items)
    return result








    
        