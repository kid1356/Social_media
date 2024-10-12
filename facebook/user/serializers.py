from .models import *
from rest_framework import serializers
from rest_framework.response import Response
from pyotp import TOTP
from facebook.settings import *
from django.core.mail import EmailMessage
from django.contrib.auth import password_validation
from django.utils.crypto import get_random_string
from django.utils import timezone

class Util:
    @staticmethod
    def send_mail(data):
        email  = EmailMessage(subject=data['subject'],    # for sending emails
                              body=data['body'],
                              to= [data["to_email"]])
        email.send()




class RegisterSerilizer(serializers.ModelSerializer):
    confirm_password  = serializers.CharField(style = {'input_type':'password'}, write_only=True)
    class Meta:
        model  = User
        fields = ['email','username','first_name','last_name',
                'password','confirm_password','gender','country','city','profile_picture','biograpghy','date_of_birth' ]
        
        extra_kwargs = {
            'first_name':{'required':True},
            'password':{'write_only' :True},
            'email':{'required':True},
            'gender':{'required':True},
            
        }

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password != confirm_password:

            raise serializers.ValidationError("both passsword should be same. ")
        
        return attrs
     
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        model  = User
        fields = ['email', 'password']
        

class UserProfileSerializer(serializers.ModelSerializer):
   class Meta:
      model = User
      fields = ['id','email','first_name']


class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length = 255,style = {'input_type':'password'}, write_only = True)
    confirm_password = serializers.CharField(max_length = 255,style = {'input_type':'password'}, write_only = True)
    class Meta:
        model = User
        fields = ['password', 'confirm_password']

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        user = self.context.get('user')

        if password != confirm_password:
            raise serializers.ValidationError("Both password must be same!")
        
        user.set_password(password)
        user.save()
        return attrs        
        

class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length = 255)
    
    def validate(self, attrs):
        email = attrs.get('email')
     
        try:  
           user = User.objects.get(email = email)
        except User.DoesNotExist:
            return serializers.ValidationError("User does not Exists!")
        
    
        otp_value = get_random_string(length=4, allowed_chars='0123456789')


        data = {
            'subject':"Your Password Reset OTP",
            'body':f'Your OTP is : {otp_value}',
            'to_email':user.email
        }
        
        user.secret_key = otp_value
        user.otp_created_at = timezone.now()
        user.save()
        Util.send_mail(data)

        return attrs

class OTPVerifySerializer(serializers.Serializer):
    otp_value = serializers.CharField(max_length =26 )
    email = serializers.EmailField(max_length = 100)

    def validate(self, attrs):
        otp_value = attrs.get('otp_value')
        email = attrs.get('email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return serializers.ValidationError("User does not Exists!")
        
        if user.secret_key != otp_value:
            raise serializers.ValidationError("Invalid OTP")
        
        if user.otp_created_at + timedelta(minutes=5) < timezone.now():
            raise serializers.ValidationError("OTP is Expired")
        
        return attrs


class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length = 255)
    password = serializers.CharField(max_length = 255, style={'input_type':'password'}, write_only = True)
    confirm_password = serializers.CharField(max_length = 255, style={'input_type':'password'}, write_only = True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password !=  confirm_password:
            raise serializers.ValidationError("Both password should be equal")
        
        try:
           user= User.objects.get(email=email)

        except User.DoesNotExist:
            return serializers.ValidationError("User does not Exists!")
        
        attrs['user'] = user
        
        return attrs
    
    def create(self, validated_data):
        user = validated_data['user']
        user.set_password(validated_data['password'])

        user.secret_key = ''
        user.otp_created_at = None
        user.save()

        return user
