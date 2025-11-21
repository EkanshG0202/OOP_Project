from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.shortcuts import render

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    # This should match the callback URL you defined in Google Cloud Console
    # and the one your Frontend uses.
    callback_url = "http://localhost:5173" 
    client_class = OAuth2Client