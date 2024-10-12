from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView,TokenObtainPairView

# router = DefaultRouter()
# router.register(r'register/', RegisterView, basename='register')


urlpatterns = [
    path('register/', RegisterView.as_view(), name = 'register'),
    path('login/', LoginView.as_view(), name = 'login'),
    path('change-password/', ChangePasswordView.as_view(), name = 'change-password'),
    path('user-profile/',UserProfileView.as_view(), name="userprofile"),
    path('update/', UpdateUserInfoView.as_view(), name = 'update-info'),
    path('forget-password-email/', ForgetPasswordEmailView.as_view(), name = 'send-email'),
    path('forget-password/', ForgetPasswordView.as_view(), name = 'forget-password-recovery'),
    path('verify-otp/', OTPConfirmationView.as_view(), name = 'otp-confirmed'),
    path('admin/activate-user/<int:id>/', ActiveUserView.as_view(), name = 'active-user'),
    path('admin/deactivate-user/<int:id>/', DeActiveUserView.as_view(), name = 'de-active-user'),
    path('admin/get-all-user/', AdminGetAllUserDetailList.as_view(), name = 'get-all-user'),
    path('admin/get-user/<int:id>/', AdminUserDetailView.as_view(), name = 'get-a-user'),
    path('admin/delete-user/<int:id>/', AdminUserDeleteView.as_view(), name = 'delete-a-user'),
    path('admin/change-user-role/<int:id>/', AdminUserChangeRole.as_view(), name = 'change-user-role'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),

    #front-end url

    path('front-login/',login, name= "login-front")
    
    
]