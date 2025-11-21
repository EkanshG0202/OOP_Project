from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from django.db import transaction
from .models import User, CustomerProfile, RetailerProfile, WholesalerProfile

# --- IMPORT GEOPY ---
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
# --------------------

class CustomRegisterSerializer(RegisterSerializer):
    """
    Overrides the default dj-rest-auth serializer to include
    role selection and profile creation.
    """
    
    # --- New fields to accept during registration ---
    
    # 1. The role
    role = serializers.ChoiceField(choices=User.Role.choices)
    
    # 2. CustomerProfile fields
    phone_number = serializers.CharField(max_length=15, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    
    # 3. RetailerProfile fields
    shop_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    # --- MODIFIED: We accept the text address to calculate coordinates ---
    shop_address = serializers.CharField(max_length=255, required=False, allow_blank=True)
    
    # 4. WholesalerProfile fields
    business_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    warehouse_location = serializers.CharField(max_length=255, required=False, allow_blank=True)

    # --- HELPER FUNCTION FOR GEOCODING (FREE) ---
    def get_lat_lon(self, address_string):
        """
        Converts an address string to (lat, lon) using OpenStreetMap (Nominatim).
        No API key required.
        """
        if not address_string:
            return None, None
            
        try:
            # IMPORTANT: Provide a unique user_agent to identify your app
            geolocator = Nominatim(user_agent="livemart_project_edu_app")
            
            # timeout=10 prevents hanging if the free service is slow
            location = geolocator.geocode(address_string, timeout=10)
            
            if location:
                return location.latitude, location.longitude
            else:
                print(f"Warning: Address '{address_string}' could not be geocoded.")
                return None, None
                
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"Geocoding service error: {e}")
            return None, None
    # --------------------------------------------

    @transaction.atomic
    def save(self, request):
        """
        This is the core logic.
        1. Call the parent 'save' to create the User.
        2. Get the 'role' from validated_data.
        3. Set the user's role.
        4. Create the correct profile based on the role.
        """
        
        # 1. Create the User
        user = super().save(request)
        
        # 2. Get the role
        role = self.validated_data.get('role')
        
        # 3. Set the user's role
        user.role = role
        user.save()
        
        # 4. Create the appropriate profile
        try:
            if role == User.Role.CUSTOMER:
                CustomerProfile.objects.create(
                    user=user,
                    phone_number=self.validated_data.get('phone_number', ''),
                    address=self.validated_data.get('address', '')
                )
            
            elif role == User.Role.RETAILER:
                shop_name = self.validated_data.get('shop_name')
                shop_address = self.validated_data.get('shop_address', '')

                if not shop_name:
                    raise serializers.ValidationError({'shop_name': 'Shop name is required for retailers.'})
                
                # --- GEOCODING LOGIC ---
                # Calculate coordinates from the address
                lat, lon = self.get_lat_lon(shop_address)
                
                RetailerProfile.objects.create(
                    user=user,
                    shop_name=shop_name,
                    shop_address=shop_address,
                    location_lat=lat, # Saved automatically
                    location_lon=lon  # Saved automatically
                )
            
            elif role == User.Role.WHOLESALER:
                business_name = self.validated_data.get('business_name')
                if not business_name:
                    raise serializers.ValidationError({'business_name': 'Business name is required for wholesalers.'})

                WholesalerProfile.objects.create(
                    user=user,
                    business_name=business_name,
                    warehouse_location=self.validated_data.get('warehouse_location', '')
                )
        except Exception as e:
            # If profile creation fails, roll back the user creation
            raise serializers.ValidationError(f"Failed to create profile: {str(e)}")

        return user