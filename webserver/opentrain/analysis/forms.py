from django import forms
from bootstrap3_datetime.widgets import DateTimePicker

def get_labels():
    import models
    qs = models.AnalysisMarker.objects.all().values_list('label',flat=True).distinct()
    result = [(x,x) for x in qs]
    return result

def get_device_ids_summary():
    result = []
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("""
        SELECT device_id,MIN(DATE(timestamp)) as device_date,
        COUNT(*) from analysis_report 
        GROUP BY device_id 
        ORDER BY device_date
    """)
    tuples = cursor.fetchall()
    for t in tuples:
        tuple_id = '%s::::%s:%s:%s' % (t[0],t[1].year,t[1].month,t[1])
        tuple_print = '%s @%s (%d)' % t
        result.append((tuple_id,tuple_print))
    return result
        
class LabelsForm(forms.Form):
    labels = forms.ChoiceField(choices=get_labels())
    
class ReportsForm(forms.Form):
    device_desc = forms.ChoiceField(choices=get_device_ids_summary(),label='Device Id')
    start_time = forms.DateTimeField(
                                            input_formats = ['%Y-%m-%d %H:%M'],
                                            required=False,
                                            widget=DateTimePicker(options={"format": "YYYY-MM-DD HH:mm",
                                                                           "pickTime": True,
                                                                           "pickSeconds" : False}))

    end_time = forms.DateTimeField(
                                            input_formats = ['%Y-%m-%d %H:%M'],
                                            required=False,
                                            widget=DateTimePicker(options={"format": "YYYY-MM-DD HH:mm",
                                                                           "pickTime": True,
                                                                           "pickSeconds" : False}))

    
class ReportDetailForm(forms.Form):
    report_id = forms.CharField(max_length=20,label='Report ID')
    def clean_report_id(self):
        import models
        data = self.cleaned_data['report_id']
        if not models.Report.objects.filter(id=data).exists():
            raise forms.ValidationError("No Report with such id")
        # Always return the cleaned data, whether you have changed it or
        # not.
        return data

    
    
     
    
    

