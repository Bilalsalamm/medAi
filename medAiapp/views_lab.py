from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PatientForm, ReportForm
from .models import Report
from django.contrib.auth.models import User

@login_required
def lab_dashboard(request):
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'lab_assistant':
        return redirect('login')
    if request.method == 'POST':
        patient_form = PatientForm(request.POST)
        report_form = ReportForm(request.POST, request.FILES)
        if patient_form.is_valid() and report_form.is_valid():
            patient = patient_form.save()
            report = report_form.save(commit=False)
            report.patient = patient
            report.uploaded_by = request.user
            report.save()
            return redirect('lab_dashboard')
    else:
        patient_form = PatientForm()
        report_form = ReportForm()
    reports = Report.objects.filter(uploaded_by=request.user).order_by('-created_at')
    return render(request, 'lab_dashboard.html', {
        'patient_form': patient_form,
        'report_form': report_form,
        'reports': reports,
    })
