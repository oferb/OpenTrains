from django import forms

def get_labels():
    import models
    qs = models.AnalysisMarker.objects.all().values_list('label',flat=True).distinct()
    result = [(x,x) for x in qs]
    return result

def get_pairs():
    import models
    reports = models.Report.objects.all()
    device_ids = set(reports.values_list('device_id',flat=True))
    print '# of device ids = %d' % (len(device_ids))
    pairs = []
    for device_id in device_ids:
        device_times =  list(models.Report.objects.filter(device_id=device_id).order_by('timestamp').values_list('timestamp',flat=True))
        selected_times = []
        selected_times.append(device_times[0])
        pairs.append('%s @%s' % (device_id,device_times[0]))
        #for t in device_times:
        #    if (t - selected_times[-1]).total_seconds() > 7200:
        #        selected_times.append(t)
        #        pairs.append('%s %s' % (device_id,t))                         
    result = [(p,p) for p in pairs]
    print result
    return result
    
class LabelsForm(forms.Form):
    labels = forms.ChoiceField(choices=get_labels())
    
class ReportsForm(forms.Form):
    pair = forms.ChoiceField(choices=get_pairs())
    
    

