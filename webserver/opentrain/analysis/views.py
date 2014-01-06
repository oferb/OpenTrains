from django.shortcuts import render
import forms
# Create your views here.

def show_labels(req):
    ctx = dict(form=forms.LabelsForm)
    return render(req,'analysis/show_labels.html',ctx)

def show_reports(req):
    ctx = dict(form=forms.ReportsForm)
    return render(req,'analysis/show_reports.html',ctx)




