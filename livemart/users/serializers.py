from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from django.db import transaction
from .models import User, CustomerProfile, RetailerProfile, WholesalerProfile

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
    location_lat = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    location_lon = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    
    # 4. WholesalerProfile fields
    business_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    warehouse_location = serializers.CharField(max_length=255, required=False, allow_blank=True)

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
                if not shop_name:
                    # We can enforce required fields for certain roles
                    raise serializers.ValidationError({'shop_name': 'Shop name is required for retailers.'})
                
                RetailerProfile.objects.create(
                    user=user,
                    shop_name=shop_name,
                    location_lat=self.validated_data.get('location_lat'),
                    location_lon=self.validated_data.get('location_lon')
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