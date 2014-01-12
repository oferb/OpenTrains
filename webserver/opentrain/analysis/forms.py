from django import forms

def get_labels():
    import models
    qs = models.AnalysisMarker.objects.all().values_list('label',flat=True).distinct()
    result = [(x,x) for x in qs]
    return result

def get_device_ids():
    import models
    qs = models.Report.objects.all().values_list('device_id',flat=True).distinct()
    result = [(x,x) for x in qs]
    return result

def get_dates():
    import models
    times =  models.Report.objects.order_by('timestamp').values_list('timestamp',flat=True)
    selected_times = []
    selected_times.append(times[0])
    for t in times:
        if (t - selected_times[-1]).total_seconds() > 7200:
            selected_times.append(t)
            
    result = [(x,x) for x in selected_times]
            
    return result
    
class LabelsForm(forms.Form):
    labels = forms.ChoiceField(choices=get_labels())
    
class ReportsForm(forms.Form):
    device_id = forms.ChoiceField(choices=get_device_ids())
    timestamp = forms.ChoiceField(choices=get_dates())
    

