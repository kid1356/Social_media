from datetime import timedelta
import hashlib
from django.shortcuts import render
from user.models import User
from .serializers import Util,UserProfileSerializer,RegisterSerilizer,LoginSerializer,ForgetPasswordSerializer,ChangePasswordSerializer,OTPVerifySerializer,EmailSerializer
from adrf.views import APIView 
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from user.permissions import IsOwner
from drf_yasg.utils import swagger_auto_schema
from asgiref.sync import sync_to_async
from messanger.utils import generate_key_pair
from django.utils.crypto import get_random_string
from django.utils import timezone
# Create your views here.

def login(request):
    return render(request, 'login.html')


def generated_token(user):
    refresh = RefreshToken.for_user(user)      #token for every user 

    return {
        'refresh': str(refresh),
        'access' : str(refresh.access_token),
    }


class RegisterView(APIView):
    async def post(self, request):
        try:
            serializer = RegisterSerilizer(data = request.data)
            await sync_to_async(serializer.is_valid)(raise_exception=True)

            validated_data = serializer.validated_data.copy()
            validated_data.pop('confirm_password')
              
               
            private_key, public_key= generate_key_pair()

            user =  await sync_to_async(User.objects.create_user)(**validated_data)
    
            user.private_key = private_key
            user.public_key = public_key
            await sync_to_async(user.save)()
        

            data, token = await sync_to_async(lambda: (RegisterSerilizer(user).data, generated_token(user)))()

            return Response({"token":token,'register successfully':data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error":str(e)}, status=status.HTTP_400_BAD_REQUEST)
            

class LoginView(APIView):
    @swagger_auto_schema(
            request_body=LoginSerializer,
            responses={200: LoginSerializer}
    )
    async def post(self, request):
        try:
            serializer = LoginSerializer(data = request.data)
            await sync_to_async(serializer.is_valid)(raise_exception=True)
            email = serializer.data.get('email')
            password = serializer.data.get('password')

            user = await sync_to_async(authenticate)(email=email, password=password)
            
            if user is not None:

                token=await sync_to_async(generated_token)(user)
                
                if user.is_admin:
                    message = f"welcome Admin '{user.first_name}'"
                else:
                    message = f"welcome {user.first_name}"
                return Response({'token':token,'user':{'id':user.id,'first_name':user.first_name,'email':user.email}}, status=status.HTTP_200_OK)
            return Response('Login credential is Invalid', status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error":str(e)}, status=status.HTTP_400_BAD_REQUEST)
                    

class UserProfileView(APIView):
    async def get(self,request):
        user = request.user
        serializer = await sync_to_async(lambda: UserProfileSerializer(user).data)()

        return Response({"data": serializer},status=status.HTTP_200_OK)
    
class UpdateUserInfoView(APIView):
    permission_classes =[IsAuthenticated, IsOwner]
    async def patch(self, request):
        try:
            await sync_to_async(self.check_object_permissions)(request, request.user)

            serializer =await sync_to_async(lambda: RegisterSerilizer(request.user, data = request.data, partial = True))()
            await sync_to_async(serializer.is_valid)(raise_exception=True)
            await sync_to_async(serializer.save)()
            return Response({"User Info Updated Successfully":serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)



class ChangePasswordView(APIView):

    permission_classes = [IsAuthenticated]

    async def post(self, request):
        try:
            serializer = ChangePasswordSerializer(data = request.data, context = {'user':request.user})
            await sync_to_async(serializer.is_valid)(raise_exception=True)

            return Response('Password change successfully', status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

class ForgetPasswordEmailView(APIView):
    async def post(self, request):
        try:
            serializer = EmailSerializer(data = request.data)
            await sync_to_async(serializer.is_valid)(raise_exception=True)
            email = serializer.data.get('email')

            user = await User.objects.aget(email=email)
            if user is None:
                return Response({"message":"User not Found"}, status=status.HTTP_404_NOT_FOUND)
            
            otp_value = get_random_string(length=4,allowed_chars='0123456789')
            data = {
                'subject':"Your Password Reset OTP",
                'body':f'Your OTP is : {otp_value}',
                'to_email':user.email
            }
            
            user.secret_key = hashlib.sha256(otp_value.encode()).hexdigest()
            user.otp_created_at = timezone.now()
            await user.asave()
            Util.send_mail(data)
            return Response("An email is sent Please Check Your Mail Box",status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)

class OTPConfirmationView(APIView):
    async def post(self,request):
        try:
            serializer = OTPVerifySerializer(data = request.data)
            await sync_to_async(serializer.is_valid)(raise_exception=True)
            otp_value = serializer.data.get('otp_value')
            email = serializer.data.get('email')

            try:
                user = await User.objects.only("secret_key","otp_created_at","is_active").aget(email=email)
            except User.DoesNotExist:
                return Response({"message":"User not Found"}, status=status.HTTP_404_NOT_FOUND)
            
            hash_otp = hashlib.sha256(otp_value.encode()).hexdigest()
            if user.secret_key != hash_otp:
                return Response({"message":"Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
            
            if user.otp_created_at + timedelta(minutes=5) < timezone.now():
                return Response({"message":"OTP expired, request new OTP"}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response("Your OTP is Confirmed, please reset your password",status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ForgetPasswordView(APIView):
    
    async def post(self, request):
        try:
            serializer = ForgetPasswordSerializer(data=request.data)
            await sync_to_async(serializer.is_valid)(raise_exception=True)
            
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            try:
                user= await User.objects.aget(email=email)

            except User.DoesNotExist:
                return Response({"message":"User not Found"}, status=status.HTTP_404_NOT_FOUND)
            
            await sync_to_async(user.set_password)(password)
            user.secret_key = ''
            user.otp_created_at = None
            await user.asave()
            return Response("Password change successfully", status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)



class ActiveUserView(APIView):
    permission_classes = [IsAdminUser]
    async def patch(self, request,id):
        try:
            user = await User.objects.only('is_active').aget(id=id)

        except User.DoesNotExist:
            return Response("User does not found", status=status.HTTP_404_NOT_FOUND)
        
        user.is_active = True
        await user.asave()

        return Response("user is active Successfully",status=status.HTTP_200_OK)
    
class DeActiveUserView(APIView):
    permission_classes = [IsAdminUser]

    async def patch(self,request,id):
        try:
            user =await User.objects.only('is_active').aget(id=id)
            user.is_active = False
            await user.asave()
            return Response("user in unactive successfully", status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response("User does not exists",status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

class AdminGetAllUserDetailList(APIView):
    permission_classes = [IsAdminUser]
    async def get(self, request):
        try:
            users = User.objects.only('id','email','first_name').order_by('id')
            serializer =await sync_to_async(lambda: UserProfileSerializer(users, many  =True).data)()

            return Response({"All Users:":serializer}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
               
class AdminUserDetailView(APIView):
    permission_classes =[IsAdminUser]
    async def get(self,request,id):
        try:
            user = await User.objects.aget(id=id)
            serializer = await sync_to_async(lambda: RegisterSerilizer(user).data)()

            return Response({"User detail":serializer},status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response("User does not exist",status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AdminUserDeleteView(APIView):
    permission_classes = [IsAdminUser]

    async def delete(self, request,id):
        try:
            user = await User.objects.aget(id=id)

            serializer = await sync_to_async(lambda: RegisterSerilizer(user).data)()
            deleted_user = serializer
            await user.adelete()
            return Response({"user is deleted":deleted_user}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response("User does not exist",status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AdminUserChangeRole(APIView):
    permission_classes = [IsAdminUser]

    async def patch(self, request,id):
        try:
            user= await User.objects.aget(id=id)
            user.is_admin = True
            await user.asave()

            return Response({"User role is changed": [user.email,user.first_name,user.is_admin]},status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response("User does not exist",status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
