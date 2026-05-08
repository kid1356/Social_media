from .models import User
from rest_framework import serializers
from django.core.mail import EmailMessage

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
        attrs['is_admin'] = False
        attrs['is_active'] = True

        if password != confirm_password:

            raise serializers.ValidationError("both passsword should be same. ")
        
        return attrs
    
    


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        model  = User
        fields = ['email', 'password']
    

class UserProfileSerializer(serializers.ModelSerializer):
   class Meta:
      model = User
      fields = ['id','email','first_name','profile_picture']


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
    

class OTPVerifySerializer(serializers.Serializer):
    otp_value = serializers.CharField(max_length =6 )
    email = serializers.EmailField(max_length = 100)


class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length = 255)
    password = serializers.CharField(max_length = 255, style={'input_type':'password'}, write_only = True)
    confirm_password = serializers.CharField(max_length = 255, style={'input_type':'password'}, write_only = True)

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password !=  confirm_password:
            raise serializers.ValidationError("Both password should be equal")
        
        return attrs
