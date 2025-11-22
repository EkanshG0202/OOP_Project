import requests
import urllib.parse
import webbrowser

# --- CONFIGURATION ---
BASE_URL = "http://localhost:8000"
# Your Manual Redirect URI (Must match views.py and Google Console EXACTLY)
REDIRECT_URI = "http://localhost:8000/api/auth/google/callback/" 

# Paste your Client ID here just to generate the link (It won't be sent to the server by this script)
CLIENT_ID = "681911426960-7ccp3t0up5ldpnr0lgl1p28eq57nm912.apps.googleusercontent.com"

def run_test():
    print("--- Google Login Test Script ---")
    
    # 1. Construct the Auth URL
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"redirect_uri={REDIRECT_URI}&"
        f"prompt=consent&"
        f"response_type=code&"
        f"client_id={CLIENT_ID}&"
        f"scope=openid%20email%20profile&"
        f"access_type=online"
    )
    
    print(f"\n1. I will open this URL in your browser:\n{auth_url}")
    print("\n--> Press Enter to open browser...")
    input()
    webbrowser.open(auth_url)
    
    # 2. Get the Redirected URL
    print("\n2. After logging in, you will see a 'Page Not Found' (404) page.")
    print("   COPY the entire URL from your browser's address bar and paste it below.")
    redirected_url = input("   Paste URL here: ").strip()
    
    # 3. Extract and Clean the Code
    try:
        parsed = urllib.parse.urlparse(redirected_url)
        qs = urllib.parse.parse_qs(parsed.query)
        
        if 'code' not in qs:
            print("ERROR: No 'code' found in the URL you pasted.")
            return

        # Get the code and ensure it's decoded (e.g., %2F -> /)
        raw_code = qs['code'][0]
        # Verify if it looks encoded
        if "4%2F" in raw_code:
            print("   (Detected URL encoding, fixing it...)")
            code = urllib.parse.unquote(raw_code)
        else:
            code = raw_code
            
        print(f"\n   Extracted Code: {code[:20]}...")
        
    except Exception as e:
        print(f"ERROR parsing URL: {e}")
        return

    # 4. Send to Backend
    print("\n3. Sending code to Django backend...")
    api_url = f"{BASE_URL}/api/auth/google/"
    
    try:
        response = requests.post(api_url, json={"code": code})
        
        print(f"\n--- RESPONSE ({response.status_code}) ---")
        print(response.text)
        
        if response.status_code == 200:
            print("\nSUCCESS! You are logged in. The 'key' above is your auth token.")
        else:
            print("\nFAILED. Common reasons:")
            print("1. The 'callback_url' in users/views.py does not match 'http://localhost:8000/api/auth/google/callback/'")
            print("2. The CLIENT_SECRET in settings.py is incorrect.")
            print("3. You pasted the URL too slowly (code expired).")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    run_test()