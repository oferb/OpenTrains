import json

def getReportBatches(filename = 'example_report_json.txt'):
    json_data=open(filename)
    data = json.load(json_data)
    json_data.close()
    return data["objects"];

def printLocations(report_batches):
    count = 0
    for report_batch in report_batches:
        for report in report_batch["text"]["items"]:
            count = count + 1
            print("%d, %s, %s" % (count, report["location_api"]["lat"], report["location_api"]["long"]))

def printWifis(report_batches):
    count = 0
    wifi_keys = set()
    for report_batch in report_batches:
        for report in report_batch["text"]["items"]:
            count = count + 1
            #print(report["wifi"])
            if "wifi" in report.keys():
                for wifi in report["wifi"]:
                    wifi_keys.add(wifi["key"])
                    print("%d, %s, %s" % (count, wifi["SSID"], wifi["key"]))


report_batches = getReportBatches();
printLocations(report_batches)
printWifis(report_batches)
        