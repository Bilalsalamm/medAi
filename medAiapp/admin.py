from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

from .models import PendingUser, UserProfile, Patient, Report

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ('username_display', 'email_display', 'role', 'approval_status')
	list_filter = ('role', 'approved')
	search_fields = ('user__username', 'user__email')
	actions = ['approve_users', 'reject_users']

	def username_display(self, obj):
		return obj.user.username
	username_display.short_description = 'Username'

	def email_display(self, obj):
		return obj.user.email
	email_display.short_description = 'Email'

	def approval_status(self, obj):
		if obj.approved:
			return mark_safe('<span style="color: green; font-weight: bold;">✓ Approved</span>')
		else:
			return mark_safe('<span style="color: orange; font-weight: bold;">⏳ Pending</span>')
	approval_status.short_description = 'Status'

	def approve_users(self, request, queryset):
		count = queryset.filter(approved=False).update(approved=True)
		self.message_user(request, f'✓ {count} user(s) approved! They can now login.', messages.SUCCESS)
	approve_users.short_description = "✓ Approve Selected Users"

	def reject_users(self, request, queryset):
		# Delete users that are not approved
		users_to_delete = queryset.filter(approved=False)
		count = users_to_delete.count()
		
		# Delete associated Django users too
		for profile in users_to_delete:
			profile.user.delete()
		
		self.message_user(request, f'✗ {count} user(s) deleted.', messages.WARNING)
	reject_users.short_description = "✗ Reject & Delete Selected Users"

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
	list_display = ('name', 'dob', 'created_at')
	search_fields = ('name',)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
	list_display = ('patient', 'assigned_doctor', 'uploaded_by', 'created_at')
	list_filter = ('assigned_doctor', 'uploaded_by')
	search_fields = ('patient__name',)

# PendingUser is no longer used - all user management is done through UserProfile admin