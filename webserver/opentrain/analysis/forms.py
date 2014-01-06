from django import forms

def get_labels():
    import models
    return models.AnalysisMarker.objects.all().values_list('label',flat=True).distinct()

class LabelsForm(forms.Form):
    labels = forms.ChoiceField(choices=get_labels())
    
