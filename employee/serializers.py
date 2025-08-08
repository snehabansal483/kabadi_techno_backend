from pyexpat import model
from rest_framework import serializers
from .models import  *
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth.hashers import check_password
# from django.contrib.sites.shortcuts import get_current_site
# from django.urls import reverse
# from .utils import Util

class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField(max_length = 255, min_length = 3)
    password=serializers.CharField(max_length = 68, min_length = 6, write_only=True)


    def validate_email(self,value):
        if "@" in value:
            if value[-4:] == '.com':
                pos=value.rindex('@')
                if value[pos+1:-4].isalnum():
                    return value
                else:
                    raise serializers.ValidationError("invalid email")
            else:
                raise serializers.ValidationError("invalid email")                
        else:
            raise serializers.ValidationError("invalid email")


class Employee_profile_view_serializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Employee
        fields=['id','email','kt_id','mobile_number']

class Employee_RegisterSerializer(serializers.ModelSerializer):
    dealer_email = serializers.EmailField(min_length = 2)
    password = serializers.CharField(max_length = 68, min_length = 6, write_only=True)

    class Meta:
        model = Employee
        fields = ['dealer_email','email', 'username', 'password','ProfilePic','mobile_number','aadhar_card']

    def validate(self, attrs):
        dealer_email = attrs.get('dealer_email', '')
        email = attrs.get('email', '')
        username = attrs.get('username', '')
        mobile_number = attrs.get('mobile_number', '')
        # = attrs.get('', '')
            
        return attrs
    
    def create(self, validated_data):
        return Employee.objects.create_Employee(**validated_data)

class Employee_RegenerateVerificationEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(min_length = 2)
    
    class Meta:
        model = Employee
        fields = ['email']  

class Employee_EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length = 555)

    class Meta:
        model = Employee
        fields = ['token']

class Employee_UpdateProfilePicSerializer(serializers.Serializer):
    class Meta:
        model = Employee
        fields = ('ProfilePic',)

class Employee_Updateaadhar_cardSerializer(serializers.Serializer):
    class Meta:
        model = Employee
        fields = ('aadhar_card',)

class Employee_UpdateAtrrsSerializer(serializers.ModelSerializer):
    Eid = serializers.IntegerField()
    dealer_email = serializers.EmailField(min_length = 2)
    class Meta:
        model = Employee
        fields = ['Eid','dealer_email','mobile_number',]

class Employee_RequestPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length = 2)
    
    class Meta:
        fields = ['email']

class Dealer_Employee_RequestPasswordResetEmailSerializer(serializers.Serializer):
    dealer_email = serializers.EmailField(min_length = 2)
    employee_email = serializers.EmailField(min_length = 2)
    class Meta:
        fields = ['dealer_email','employee_email']

class Employee_SetNewPassSerializer(serializers.Serializer):
    password = serializers.CharField(min_length = 8, max_length = 68, write_only=True)
    token = serializers.CharField(min_length = 1, write_only=True)
    user_id = serializers.CharField(min_length = 1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'user_id']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            id = attrs.get('user_id')

            # id = force_str(urlsafe_base64_decode(uidb64))
            user = Employee.objects.get(id = id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The Reset link is invalid', 401)

            user.set_password(password)
            user.save()
            return(user)
        except:
            raise AuthenticationFailed('The Reset link is invalid', 401)
        


class Employee_Database_Checker(serializers.ModelSerializer):
    email = serializers.EmailField(min_length = 2, write_only=True)

    class Meta:
        model = Employee
        fields = ['email']

class Employee_ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        exclude = ('password',)