from django import forms
from .models import Patient, Report

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'dob', 'details']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'details': forms.Textarea(attrs={'rows': 3}),
        }

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['patient', 'xray_image', 'description', 'assigned_doctor']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }
