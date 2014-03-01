from django import forms
from django.utils.translation import ugettext_lazy as _
            
class ReportDetailForm(forms.Form):
    report_id = forms.CharField(max_length=20,label=_('Report ID'))
    def clean_report_id(self):
        import models
        data = self.cleaned_data['report_id']
        if not models.Report.objects.filter(id=data).exists():
            raise forms.ValidationError("No Report with such id")
        # Always return the cleaned data, whether you have changed it or
        # not.
        return data

    
    
     
    
    

