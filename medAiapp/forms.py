# forms.py
from django import forms
from .models import Patient, Report, UserProfile
from django.contrib.auth.models import User

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'dob', 'details']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'details': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter medical history...'}),
        }

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['xray_image', 'description', 'modality', 'assigned_doctor']
        widgets = {
            'xray_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter findings...', 'class': 'form-control'}),
            'modality': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Cleaner way to filter: 
        # This finds Users who have a UserProfile with role 'doctor'
        doctors = User.objects.filter(userprofile__role='doctor')
        self.fields['assigned_doctor'].queryset = doctors
        
        # Customize the dropdown to show full names
        self.fields['assigned_doctor'].label_from_instance = lambda obj: f"{obj.get_full_name() or obj.username}"
        
        # Change the default empty label
        self.fields['assigned_doctor'].empty_label = "Select a Specialist"
        self.fields['assigned_doctor'].required = True