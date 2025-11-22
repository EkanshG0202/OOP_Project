from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.core import mail
import re

User = get_user_model()

class EmailVerificationFlowTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/registration/'
        self.verify_url = '/api/auth/registration/verify-email/'
        self.login_url = '/api/auth/login/'
        
        self.user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'StrongPassword123!',
            'role': 'CUSTOMER',
        }

    def test_registration_verification_login_flow(self):
        """
        Test the full flow:
        1. Register (Expect 201 Created, but NO token yet)
        2. Check that an email was sent
        3. Extract the verification key from the email
        4. Verify the email
        5. Login (Expect success and Token)
        """
        
        # --- 1. Register ---
        print("\n1. Registering user...")
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # With 'mandatory' verification, we should NOT get a key/token immediately
        self.assertNotIn('key', response.data) 
        print("   Registration successful. Login pending verification.")

        # --- 2. Check Email Sent ---
        print("2. Checking for verification email...")
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, [self.user_data['email']])
        print("   Email found in outbox.")

        # --- 3. Extract Verification Key ---
        # In a real email, this is a link. For the API, dj-rest-auth needs the 'key'.
        # The default email body contains a link like: .../account-confirm-email/MzE:1t.../
        # We need to use the allauth model to get the exact key cleanly for testing.
        from allauth.account.models import EmailAddress, EmailConfirmation
        
        user = User.objects.get(email=self.user_data['email'])
        email_address = EmailAddress.objects.get(user=user)
        confirmation = EmailConfirmation.objects.get(email_address=email_address)
        verification_key = confirmation.key
        
        print(f"   Extracted Verification Key: {verification_key}")

        # --- 4. Verify Email ---
        print("3. Verifying email...")
        verify_data = {'key': verification_key}
        response = self.client.post(self.verify_url, verify_data)
        
        if response.status_code != status.HTTP_200_OK:
            print("   Verification failed:", response.data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("   Email Verified!")

        # --- 5. Login ---
        print("4. Attempting Login...")
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('key', response.data)
        print(f"   Login Successful! Token: {response.data['key']}")