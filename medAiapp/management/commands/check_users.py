from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from medAiapp.models import PendingUser, UserProfile


class Command(BaseCommand):
    help = 'Check user accounts and test login'

    def handle(self, *args, **options):
        print("\n=== PENDING USERS ===")
        for p in PendingUser.objects.all():
            print(f"Username: {p.username} | Email: {p.email} | Role: {p.role} | Approved: {p.approved}")

        print("\n=== ACTIVE USERS ===")
        for u in User.objects.all():
            has_profile = UserProfile.objects.filter(user=u).exists()
            role = UserProfile.objects.get(user=u).role if has_profile else "NO PROFILE"
            print(f"Username: {u.username} | Email: {u.email} | Profile: {role}")

        print("\n=== TEST LOGIN ===")
        username = input("Enter username to test: ")
        password = input("Enter password to test: ")
        
        user = User.objects.filter(username=username).first()
        if user:
            auth_user = User.objects.get(username=username)
            if auth_user.check_password(password):
                print(f"✓ Password is CORRECT for {username}")
            else:
                print(f"✗ Password is WRONG for {username}")
        else:
            print(f"✗ User {username} does not exist")
