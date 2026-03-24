from django.contrib import admin

from .models import PendingUser, UserProfile, Patient, Report
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'role')
	list_filter = ('role',)
	search_fields = ('user__username', 'user__email')

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
	list_display = ('name', 'dob', 'created_at')
	search_fields = ('name',)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
	list_display = ('patient', 'assigned_doctor', 'uploaded_by', 'created_at')
	list_filter = ('assigned_doctor', 'uploaded_by')
	search_fields = ('patient__name',)

from django.contrib import messages
from django.contrib.auth.models import User

@admin.register(PendingUser)
class PendingUserAdmin(admin.ModelAdmin):
	list_display = ('username', 'email', 'created_at', 'approved')
	list_filter = ('approved', 'created_at')
	search_fields = ('username', 'email')

	actions = ['approve_users']

	def approve_users(self, request, queryset):
		approved_count = 0
		for pending_user in queryset.filter(approved=False):
			if not User.objects.filter(username=pending_user.username).exists():
				User.objects.create_user(
					username=pending_user.username,
					email=pending_user.email,
					password=pending_user.password
				)
				pending_user.approved = True
				pending_user.save()
				approved_count += 1
		self.message_user(request, f"{approved_count} user(s) approved and activated.", messages.SUCCESS)
	approve_users.short_description = "Approve selected users and activate accounts"
