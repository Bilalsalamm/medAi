# forms.py
from django import forms
from .models import Patient, Report, UserProfile
from django.contrib.auth.models import User

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'dob', 'details']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Patient Name'}),
            'dob': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'details': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter medical history...'}),
        }

class PatientSelectionForm(forms.Form):
    """Form to select an existing patient or create new"""
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.all().order_by('-id'),
        required=False,
        empty_label="-- Create New Patient --",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'patient-select'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show patient as "ID: Name (DOB)"
        self.fields['patient'].label_from_instance = lambda obj: (
            f"ID {obj.id}: {obj.name} ({obj.dob if obj.dob else 'No DOB'})"
        )
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
        
        # 1. THE FIX: Use __role__iexact to catch 'doctor', 'Doctor', or 'DOCTOR'
        doctors = User.objects.filter(userprofile__role__iexact='doctor')
        
        self.fields['assigned_doctor'].queryset = doctors
        
        # 2. THE UI FIX: Ensure we show a name even if get_full_name() is empty
        self.fields['assigned_doctor'].label_from_instance = lambda obj: (
            f"Dr. {obj.get_full_name()}" if obj.get_full_name() else f"Dr. {obj.username.title()}"
        )
        
        self.fields['assigned_doctor'].empty_label = "Select a Specialist"
        self.fields['assigned_doctor'].required = True