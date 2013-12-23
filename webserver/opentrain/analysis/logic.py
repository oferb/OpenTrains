import models
import json
import reports.models
import common.ot_utils

def analyze_raw_reports():
    items = _collect_all_items()
    for (idx,item) in enumerate(items):
        if idx % 100 == 0:
            print '%d/%d' % (idx,len(items))
        if 'wifi' in item.keys():
            dt = common.ot_utils.get_utc_time_from_timestamp(float(item['time'])/1000)
            m = models.WifiReport(device_id=item['device_id'],timestamp=dt)
            m.save()
            for wifi in item['wifi']:
                w = models.WifiInReport(SSID=wifi['SSID'],
                                 signal=wifi['signal'],
                                 frequency=wifi['frequency'],
                                 key=wifi['key'])
                m.wifi_set.add(w)


def delete_all_reports():
    common.ot_utils.delete_from_model(models.WifiInReport)
    common.ot_utils.delete_from_model(models.WifiReport)
    
def _collect_all_items():
    delete_all_reports()
    all_reports = reports.models.RawReport.objects.all()
    result = []
    for rj in all_reports:
        items = json.loads(rj.text)['items']
        result.extend(items)
    return result








    
        