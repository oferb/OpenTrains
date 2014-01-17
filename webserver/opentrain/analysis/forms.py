from django import forms

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
        SELECT device_id,DATE(timestamp) as device_date,
        COUNT(*) from analysis_report 
        GROUP BY device_id,device_date 
        ORDER BY device_date
    """)
    tuples = cursor.fetchall()
    for tuple in tuples:
        result.append('%s @%s (%d)' % (tuple[0],tuple[1],tuple[2]))
    return [(x,x) for x in result]
        
class LabelsForm(forms.Form):
    labels = forms.ChoiceField(choices=get_labels())
    
class ReportsForm(forms.Form):
    pair = forms.ChoiceField(choices=get_device_ids_summary(),label='Device Id')
    
    
    
    

