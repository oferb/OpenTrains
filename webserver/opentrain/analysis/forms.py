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
    
class LabelsForm(forms.Form):
    labels = forms.ChoiceField(choices=get_labels())
    
class ReportsForm(forms.Form):
    device_ids = forms.ChoiceField(choices=get_device_ids())

