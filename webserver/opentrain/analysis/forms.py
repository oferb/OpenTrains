from django import forms

def get_labels():
    import models
    qs = models.AnalysisMarker.objects.all().values_list('label',flat=True).distinct()
    result = [(x,x) for x in qs]
    return result

def get_paris():
    import models
    device_ids = [models.Report.objects.all().values_list('device_id',flat=True).distinct()]
    pairs = []
    for device_id in devicde_ids:
        device_times =  models.Report.objects.filter(device_id=device_id).order_by('timestamp').values_list('timestamp',flat=True)
        selected_times = []
        selected_times.append(times[0])
        for t in times:
            if (t - selected_times[-1]).total_seconds() > 7200:
                selected_times.append(t)
                pairs.append('%s %s' % (device_id,t)
        
    for p in pairs:       
        return (p,p)
    
class LabelsForm(forms.Form):
    labels = forms.ChoiceField(choices=get_labels())
    
class ReportsForm(forms.Form):
    pairs = forms.ChoiceField(choices=get_pairs))
    
    

