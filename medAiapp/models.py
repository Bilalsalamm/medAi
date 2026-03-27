from django.db import models



from django.contrib.auth.models import User
class UserProfile(models.Model):
	ROLE_CHOICES = [
		('lab_assistant', 'Lab Assistant'),
		('doctor', 'Doctor'),
		('admin', 'Admin'),
	]
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	role = models.CharField(max_length=20, choices=ROLE_CHOICES)

	def __str__(self):
		return f"{self.user.username} ({self.role})"

class Patient(models.Model):
	name = models.CharField(max_length=150)
	dob = models.DateField(null=True, blank=True)
	details = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name

class Report(models.Model):
	MODALITY_CHOICES = [
		('Fracture', 'Bone Fracture'),
		('MRI', 'Brain MRI'),
		('Skin', 'Skin Lesion'),
		('XRay', 'Chest X-Ray'),
	]
	patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='reports')
	uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_reports')
	assigned_doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='doctor_reports')
	xray_image = models.ImageField(upload_to='xray_reports/')
	description = models.TextField(blank=True)
	modality = models.CharField(max_length=50, choices=MODALITY_CHOICES, default='XRay')
	created_at = models.DateTimeField(auto_now_add=True)
	ai_result = models.TextField(blank=True)
	ai_prediction_label = models.CharField(max_length=255, blank=True, null=True)
	ai_confidence_score = models.CharField(max_length=50, blank=True, null=True)
	ai_analysis = models.TextField(blank=True)
	ai_report = models.TextField(blank=True)
	ai_prediction_generated_at = models.DateTimeField(blank=True, null=True)

	def __str__(self):
		return f"Report for {self.patient.name} ({self.created_at.date()})"

class PendingUser(models.Model):
	username = models.CharField(max_length=150, unique=True)
	email = models.EmailField(unique=True)
	password = models.CharField(max_length=128)
	created_at = models.DateTimeField(auto_now_add=True)
	approved = models.BooleanField(default=False)

	def __str__(self):
		return self.username
