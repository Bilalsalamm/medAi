
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
def logout_view(request):
    auth_logout(request)
    return redirect('login')

def home(request):
    return render(request, 'homepage.html')
def dashboard(request):
    user = request.user
    context = {'user': user}
    
    # Only run this logic for Doctors
    if hasattr(user, 'userprofile') and user.userprofile.role == 'doctor':
        from medAiapp.models import Report, Patient
        
        # 1. Get reports assigned to this doctor that HAVE a patient linked
        # This prevents the 'blank' rows you saw in the screenshot
        reports = Report.objects.filter(
            assigned_doctor=user, 
            patient__isnull=False 
        ).select_related('patient').order_by('-created_at')

        # 2. Group them by patient so one patient doesn't show up twice
        patients_map = {}
        for report in reports:
            if report.patient_id not in patients_map:
                patients_map[report.patient_id] = {
                    'patient_obj': report.patient,  # Storing the actual Patient object
                    'last_report': report
                }
        
        # 3. Calculate metrics
        context['assigned_patients'] = list(patients_map.values())
        context['total_patients'] = len(patients_map)  # Unique patients
        context['total_reports'] = reports.filter(ai_prediction_label__isnull=False).count()  # Analyzed reports
        context['pending_reports'] = reports.filter(ai_prediction_label__isnull=True).count()  # Pending analysis

    return render(request, 'dashboard.html', context)

def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user profile is approved
            try:
                profile = user.userprofile
                if not profile.approved:
                    error = '⏳ Your account is pending admin approval. Please wait.'
                    return render(request, 'login.html', {'error': error})
            except:
                error = '❌ User profile not found. Please contact admin.'
                return render(request, 'login.html', {'error': error})
            
            # User approved - login
            auth_login(request, user)
            
            # Redirect based on role
            try:
                role = user.userprofile.role
                if role == 'lab_assistant':
                    return redirect('lab_dashboard')
                elif role == 'doctor':
                    return redirect('dashboard')
                else:
                    return redirect('dashboard')
            except Exception:
                return redirect('dashboard')
        else:
            error = '❌ Invalid username or password.'
    
    return render(request, 'login.html', {'error': error})

def forgot_password(request):
    from django.contrib.auth.models import User
    from medAiapp.models import PasswordResetOTP
    from django.core.mail import send_mail
    import random
    
    message = None
    error = None
    
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # Check if email exists and user is approved
        try:
            user = User.objects.get(email=email)
            profile = user.userprofile
            
            # Only allow approved users to reset password
            if not profile.approved:
                error = '❌ Your account is not yet approved for password reset. Please contact admin.'
        except User.DoesNotExist:
            error = '❌ This email is not registered in our system.'
        except:
            error = '❌ User profile not found. Please contact admin.'
        
        if not error:
            try:
                # Generate 6-digit OTP
                otp = str(random.randint(100000, 999999))
                
                # Delete any existing OTPs for this email
                PasswordResetOTP.objects.filter(email=email).delete()
                
                # Create new OTP
                otp_record = PasswordResetOTP.objects.create(email=email, otp=otp)
                
                # Send OTP via email
                subject = "Password Reset OTP - Med AI"
                message_body = f"""
Hello,

Your password reset OTP is: {otp}

This OTP will expire in 10 minutes. Please do not share this code with anyone.

If you didn't request this, please ignore this email.

Best regards,
Med AI Team
                """
                
                send_mail(
                    subject,
                    message_body,
                    'noreply@medai.com',
                    [email],
                    fail_silently=False,
                )
                
                # Redirect to OTP verification page
                return redirect(f'/verify-otp/?email={email}')
                
            except Exception as e:
                error = f'Error sending OTP: {str(e)}'
    
    return render(request, 'forgot_password.html', {'message': message, 'error': error})

def reset_password(request, token):
    from medAiapp.models import PasswordResetToken
    
    error = None
    message = None
    
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        
        # Check if token is expired
        if reset_token.is_expired:
            error = '❌ This reset link has expired. Please request a new one.'
            return render(request, 'reset_password.html', {'error': error, 'expired': True})
        
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if new_password != confirm_password:
                error = '❌ Passwords do not match.'
            elif len(new_password) < 8:
                error = '❌ Password must be at least 8 characters long.'
            else:
                # Update password
                user = reset_token.user
                user.set_password(new_password)
                user.save()
                
                # Delete the token
                reset_token.delete()
                
                message = '✓ Password reset successfully! You can now login with your new password.'
                return render(request, 'password_reset_success.html', {'message': message})
        
        return render(request, 'reset_password.html', {'token': token})
    
    except PasswordResetToken.DoesNotExist:
        error = '❌ Invalid reset link. Please request a new password reset.'
        return render(request, 'reset_password.html', {'error': error, 'expired': True})

def verify_otp(request):
    from medAiapp.models import PasswordResetOTP
    from django.contrib.auth.models import User
    
    email = request.GET.get('email')
    error = None
    message = None
    
    if not email:
        error = '❌ Email not found. Please try again.'
        return redirect('/forgot-password/')
    
    # Check if email exists and user is approved
    try:
        user = User.objects.get(email=email)
        profile = user.userprofile
        
        if not profile.approved:
            error = '❌ Your account is not approved. Cannot reset password.'
            return render(request, 'verify_otp.html', {'error': error, 'email': email})
    except User.DoesNotExist:
        error = '❌ This email is not registered.'
        return render(request, 'verify_otp.html', {'error': error, 'email': email})
    except:
        error = '❌ User profile not found.'
        return render(request, 'verify_otp.html', {'error': error, 'email': email})
    
    if request.method == 'POST':
        otp_code = request.POST.get('otp')
        
        try:
            # Get the latest OTP for this email
            otp_record = PasswordResetOTP.objects.filter(email=email).latest('created_at')
            
            # Check if OTP is still valid
            if otp_record.is_expired:
                error = '❌ OTP has expired. Please request a new one.'
            elif otp_record.attempts >= 5:
                error = '❌ Too many incorrect attempts. Please request a new OTP.'
            elif otp_record.otp != otp_code:
                otp_record.attempts += 1
                otp_record.save()
                error = f'❌ Incorrect OTP. Attempts remaining: {5 - otp_record.attempts}'
            else:
                # OTP is correct
                otp_record.verified = True
                otp_record.save()
                # Redirect to reset password page
                return redirect(f'/reset-password-otp/?email={email}')
        
        except PasswordResetOTP.DoesNotExist:
            error = '❌ OTP not found. Please request a new one.'
    
    return render(request, 'verify_otp.html', {'email': email, 'error': error})

def reset_password_otp(request):
    from medAiapp.models import PasswordResetOTP
    from django.contrib.auth.models import User
    
    email = request.GET.get('email')
    error = None
    message = None
    
    if not email:
        error = '❌ Email not found. Please try again.'
        return redirect('/forgot-password/')
    
    try:
        # Check if OTP was verified
        otp_record = PasswordResetOTP.objects.filter(email=email).latest('created_at')
        
        if not otp_record.verified:
            error = '❌ Please verify your OTP first.'
            return redirect(f'/verify-otp/?email={email}')
        
        # Check if user is approved
        user = User.objects.get(email=email)
        profile = user.userprofile
        
        if not profile.approved:
            error = '❌ Your account is not approved. Cannot reset password.'
            return render(request, 'reset_password_otp.html', {'error': error, 'email': email})
        
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if new_password != confirm_password:
                error = '❌ Passwords do not match.'
            elif len(new_password) < 8:
                error = '❌ Password must be at least 8 characters long.'
            else:
                # Get user and update password
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                
                # Delete the OTP record
                otp_record.delete()
                
                # Redirect to success page
                return render(request, 'password_reset_success.html', {'message': '✓ Password reset successfully! You can now login with your new password.'})
        
        return render(request, 'reset_password_otp.html', {'email': email})
    
    except (PasswordResetOTP.DoesNotExist, User.DoesNotExist):
        error = '❌ Invalid request. Please try again.'
        return redirect('/forgot-password/')

from .models import PendingUser

def register(request):
    error = None
    message = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        role = request.POST.get('role', 'doctor')
        
        from django.contrib.auth.models import User
        
        if User.objects.filter(username=username).exists():
            error = 'Username already exists.'
        elif User.objects.filter(email=email).exists():
            error = 'Email already exists.'
        else:
            try:
                # 1. Create Django User
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                
                # 2. Create UserProfile with role (not approved yet)
                from medAiapp.models import UserProfile
                UserProfile.objects.create(
                    user=user,
                    role=role,
                    approved=False  # Waiting for admin approval
                )
                
                message = '✓ Registration submitted! Awaiting admin approval. You will receive access once approved.'
            except Exception as e:
                error = f'Error during registration: {str(e)}'
    
    return render(request, 'register.html', {'error': error, 'message': message})