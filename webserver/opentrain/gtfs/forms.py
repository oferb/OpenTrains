from django import forms
from bootstrap3_datetime.widgets import DateTimePicker

class SearchBetweenForm(forms.Form):
    import logic
    from_station = forms.ChoiceField(choices=logic.get_stations_choices())
    to_station = forms.ChoiceField(choices=logic.get_stations_choices())
    before = forms.IntegerField()
    after = forms.IntegerField()
    when = forms.DateTimeField(
        input_formats = ['%Y-%m-%d %H:%M'],
        widget=DateTimePicker(options={"format": "YYYY-MM-DD HH:mm",
                                       "pickTime": True,
                                       "pickSeconds" : False}))

    
class SearchInForm(forms.Form):
    import logic
    in_station = forms.ChoiceField(choices=logic.get_stations_choices())
    before = forms.IntegerField()
    after = forms.IntegerField()
    when = forms.DateTimeField(
        input_formats = ['%Y-%m-%d %H:%M'],
        widget=DateTimePicker(options={"format": "YYYY-MM-DD HH:mm",
                                       "pickTime": True,
                                       "pickSeconds" : False}))
    
    