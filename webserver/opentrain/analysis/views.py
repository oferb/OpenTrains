from django.shortcuts import render
import forms
# Create your views here.

def labels_map(req):
    ctx = dict(form=forms.LabelsForm)
    return render(req,'analysis/show_labels.html',ctx)





