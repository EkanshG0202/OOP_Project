from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings

class CustomGoogleOAuth2Client(OAuth2Client):
    # --- FIX: Added 'scope' as a positional argument before 'scope_delimiter' ---
    def __init__(self, request, consumer_key, consumer_secret, access_token_method, access_token_url, callback_url, scope=None, scope_delimiter=" ", headers=None, basic_auth=False):
        # We capture 'scope' and 'scope_delimiter' here to satisfy dj-rest-auth,
        # but we do NOT pass them to super() because django-allauth dropped them.
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

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = CustomGoogleOAuth2Client
    
    # Ensure this matches what you put in Google Cloud Console
    callback_url = "http://localhost:8000/api/auth/google/callback/"