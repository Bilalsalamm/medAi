from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from medAiapp.models import PendingUser, UserProfile


class Command(BaseCommand):
    help = 'Fix: Create missing UserProfiles for approved users'

    def handle(self, *args, **options):
        print("\n=== CHECKING APPROVED USERS ===\n")
        
        approved_pending_users = PendingUser.objects.filter(approved=True)
        
        if not approved_pending_users.exists():
            print("No approved pending users found.")
            return
        
        fixed_count = 0
        for pending_user in approved_pending_users:
            user = User.objects.filter(username=pending_user.username).first()
            
            if user:
                # Check if UserProfile exists
                profile = UserProfile.objects.filter(user=user).first()
                
                if profile:
                    print(f"✓ {pending_user.username} - Has UserProfile (Role: {profile.role})")
                else:
                    # Create missing UserProfile
                    UserProfile.objects.create(
                        user=user,
                        role=pending_user.role
                    )
                    print(f"✓ FIXED: Created UserProfile for {pending_user.username} (Role: {pending_user.role})")
                    fixed_count += 1
            else:
                print(f"✗ {pending_user.username} - NO Django User found!")
        
        print(f"\n=== RESULT: Fixed {fixed_count} missing profiles ===\n")
        
        # Show summary
        print("=== ALL ACTIVE USERS ===\n")
        for u in User.objects.all():
            profile = UserProfile.objects.filter(user=u).first()
            role = profile.role if profile else "❌ NO PROFILE"
            print(f"  {u.username} ({u.email}) - {role}")
