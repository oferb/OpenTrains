from django import forms
from bootstrap3_datetime.widgets import DateTimePicker

class SearchBetweenForm(forms.Form):
    import logic
    from_station = forms.ChoiceField(choices=logic.get_stations_choices())
    to_station = forms.ChoiceField(choices=logic.get_stations_choices())
    when = forms.DateField(
        widget=DateTimePicker(options={"format": "YYYY-MM-DD HH:mm",
                                       "pickTime": True,
                                       "pickSeconds" : False}))

    
class SearchInForm(forms.Form):
    import logic
    in_station = forms.ChoiceField(choices=logic.get_stations_choices())
    when = forms.DateField(
        widget=DateTimePicker(options={"format": "YYYY-MM-DD HH:mm",
                                       "pickTime": True,
                                       "pickSeconds" : False}))
    
    