from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
import requests

class CustomGoogleOAuth2Client(OAuth2Client):
    def __init__(self, request, consumer_key, consumer_secret, access_token_method, access_token_url, callback_url, scope=None, scope_delimiter=" ", headers=None, basic_auth=False):
        # 1. Fix for the "scope_delimiter" crash
        super().__init__(
            request=request,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token_method=access_token_method,
            access_token_url=access_token_url,
            callback_url=callback_url,
            headers=headers,
            basic_auth=basic_auth
        )

    # 2. Debugging Method to see Google's error response
    def get_access_token(self, code):
        # Construct the data payload exactly as allauth does
        data = {
            "client_id": self.consumer_key,
            "client_secret": self.consumer_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.callback_url,
        }
        
        # --- PRINT DEBUG INFO ---
        print("\n" + "="*40)
        print("[DEBUG] DJANGO IS SENDING THIS TO GOOGLE:")
        print(f" - Target URL: {self.access_token_url}")
        print(f" - Redirect URI: '{self.callback_url}'")
        # Mask keys for safety
        print(f" - Client ID: {self.consumer_key[:15]}..." if self.consumer_key else " - Client ID: NONE (Check .env/settings!)")
        print(f" - Client Secret: {self.consumer_secret[:5]}..." if self.consumer_secret else " - Client Secret: NONE (Check .env/settings!)")
        print(f" - Authorization Code: {code}")
        print("="*40 + "\n")

        # Send the request manually
        response = requests.post(self.access_token_url, data=data)
        
        # --- PRINT GOOGLE RESPONSE ---
        print("\n" + "="*40)
        print(f"[DEBUG] GOOGLE RESPONDED ({response.status_code}):")
        try:
            print(response.json())
        except:
            print(response.text)
        print("="*40 + "\n")

        # Return result to the parent class logic
        if response.status_code == 200:
            return response.json()
        else:
            return None

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = CustomGoogleOAuth2Client
    
    # --- CRITICAL: MUST MATCH GOOGLE CONSOLE EXACTLY (Check for trailing slash) ---
    callback_url = "http://localhost:8000/api/auth/google/callback/"