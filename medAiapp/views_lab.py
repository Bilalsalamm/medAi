from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import PatientForm, ReportForm
from .models import Report, Patient, UserProfile
from django.contrib.auth.models import User
from django.contrib import messages # Added for feedback

@login_required
def lab_dashboard(request):
    # Role Check
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'lab_assistant':
        return redirect('login')

    patient_edit = None
    patient_id = request.GET.get('edit_patient')
    
    # Handle GET request for editing a patient
    if patient_id:
        patient_edit = get_object_or_404(Patient, id=patient_id)

    if request.method == 'POST':
        # --- CASE 1: UPDATING AN EXISTING PATIENT ---
        if 'edit_patient_id' in request.POST:
            patient_to_edit = get_object_or_404(Patient, id=request.POST['edit_patient_id'])
            patient_form = PatientForm(request.POST, instance=patient_to_edit)
            if patient_form.is_valid():
                patient_form.save()
                messages.success(request, "Patient details updated successfully.")
                return redirect('lab_dashboard')

        # --- CASE 2: UPLOADING A NEW REPORT ---
        else:
            patient_form = PatientForm(request.POST)
            report_form = ReportForm(request.POST, request.FILES)

            # We check if report_form is valid first. 
            # Since we 'excluded' patient in forms.py, it will now pass.
            if report_form.is_valid():
                if patient_form.is_valid():
                    # Save the new patient
                    patient = patient_form.save()
                    
                    # Create the report object but don't save to DB yet
                    report = report_form.save(commit=False)
                    report.patient = patient
                    report.uploaded_by = request.user
                    report.save()
                    
                    messages.success(request, f"Report for {patient.name} uploaded successfully!")
                    return redirect('lab_dashboard')
                else:
                    # If patient form is invalid, the page will re-render with errors
                    messages.error(request, "Please correct the errors in the patient form.")
            else:
                messages.error(request, "Please correct the errors in the report form.")

    else:
        # GET Request: Initial empty forms
        patient_form = PatientForm(instance=patient_edit) if patient_edit else PatientForm()
        report_form = ReportForm()

    # Always fetch the latest data for the tabs
    patients = Patient.objects.all().order_by('-id') 
    reports = Report.objects.filter(uploaded_by=request.user).order_by('-created_at')
    doctors = User.objects.filter(userprofile__role='doctor')

    return render(request, 'lab_dashboard.html', {
        'patient_form': patient_form,
        'report_form': report_form,
        'reports': reports,
        'patients': patients,
        'patient_edit': patient_edit,
        'doctors': doctors,
    })
@login_required
def patient_detail(request, patient_id):
    from .ai_service import get_ai_prediction
    from django.utils import timezone
    import logging
    
    logger = logging.getLogger(__name__)
    patient = get_object_or_404(Patient, id=patient_id)
    
    # Get all reports for this patient
    reports = patient.reports.all()
    
    # Generate AI predictions on-demand for reports without predictions
    # But don't block page render if API is slow
    for report in reports:
        if not report.ai_prediction_label and report.xray_image:
            try:
                logger.info(f"Attempting AI prediction for report {report.id} with modality: {report.modality}")
                # Call Kaggle API for prediction with modality
                prediction = get_ai_prediction(report.xray_image.name, modality=report.modality)
                
                if prediction:
                    logger.info(f"Prediction successful for report {report.id}: {prediction}")
                    report.ai_prediction_label = prediction.get('diagnosis', 'Unable to predict')
                    report.ai_confidence_score = prediction.get('confidence', '0%')
                    report.ai_analysis = prediction.get('modality', report.modality)
                    report.ai_report = prediction.get('report', '')
                    report.ai_prediction_generated_at = timezone.now()
                    report.save()
                    logger.info(f"Saved prediction for report {report.id}")
                else:
                    logger.warning(f"No prediction returned for report {report.id}")
            except Exception as e:
                logger.error(f"Error getting AI prediction for report {report.id}: {str(e)}")
                # Don't crash - just skip the prediction
                continue
    
    return render(request, 'patient_detail.html', {'patient': patient})

@login_required
def doctor_patients(request):
    # Only allow doctors to view their assigned patients
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'doctor':
        return redirect('login')
    # Get all reports assigned to this doctor
    reports = Report.objects.filter(assigned_doctor=request.user).select_related('patient').order_by('-created_at')
    # Get unique patients from these reports
    patients = {report.patient for report in reports}
    return render(request, 'doctor_patients.html', {'patients': patients, 'reports': reports})