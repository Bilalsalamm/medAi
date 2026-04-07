from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import uuid


class UserProfile(models.Model):
	ROLE_CHOICES = [
		('lab_assistant', 'Lab Assistant'),
		('doctor', 'Doctor'),
		('admin', 'Admin'),
	]
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	role = models.CharField(max_length=20, choices=ROLE_CHOICES)
	approved = models.BooleanField(default=False)  # Approval status

	def __str__(self):
		status = "✓ Approved" if self.approved else "⏳ Pending"
		return f"{self.user.username} ({self.role}) - {status}"

	class Meta:
		ordering = ('user__date_joined',)

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

# models.py
class PendingUser(models.Model):
    ROLE_CHOICES = [
        ('lab_assistant', 'Lab Assistant'),
        ('doctor', 'Doctor'),
    ]
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    
    # ADD THIS: Captures the requested role
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='doctor') 
    
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True, null=True)  # Optional rejection reason

    def __str__(self):
        return f"{self.username} ({self.role})"

class PasswordResetToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='password_reset_token')
    token = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def is_expired(self):
        # Token expires after 24 hours
        return timezone.now() - self.created_at > timedelta(hours=24)
    
    def __str__(self):
        return f"Reset token for {self.user.username}"

class PasswordResetOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    
    @property
    def is_expired(self):
        # OTP expires after 10 minutes
        return timezone.now() - self.created_at > timedelta(minutes=10)
    
    @property
    def is_valid(self):
        # Valid if not expired, not verified, and attempts < 5
        return not self.is_expired and not self.verified and self.attempts < 5
    
    def __str__(self):
        return f"OTP for {self.email}"
    
    class Meta:
        ordering = ['-created_at']
