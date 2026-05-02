from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self,email,password=None,**extra_fields):

        if not email:
            raise ValueError("User must have an Email")
        
        user = self.model(
            email = self.normalize_email(email), **extra_fields )

        user.set_password(password)
        user.save(using= self._db)
        return user

    def create_superuser(self, email,password=None, **extra_fields):

        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(
            email = email,
            password = password,
            **extra_fields
        )
    
class User(AbstractBaseUser,PermissionsMixin):
    CHOICE_FIELDS  = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('None', 'None')
    )
    username = models.CharField(max_length = 200, null = True, blank = True)
    email = models.EmailField (max_length = 255,  unique = True)
    gender = models.CharField(max_length= 100 ,choices = CHOICE_FIELDS)
    first_name = models.CharField(max_length = 150, null=True, blank = True)
    last_name = models.CharField(max_length = 150, null = True, blank = True)
    profile_picture = models.ImageField(upload_to='images/',default='default.jpeg', blank=True , null=True)
    date_of_birth  = models.DateField(blank = True, null = True)
    city = models.CharField(max_length=255, blank = True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    biograpghy = models.TextField(max_length = 500, blank = True, null=True)
    secret_key = models.CharField(max_length = 16,null = True, blank = True)
    otp_created_at = models.DateTimeField(null=True,blank=True)
    public_key = models.TextField(null=True,blank=True)
    private_key = models.TextField(null=True,blank=True)
    created_at  = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
      return self.email

    def has_perm(self, perm, obj=None):
     "Does the user have a specific permission?"
      # Simplest possible answer: Yes, always
     return self.is_admin or self.is_superuser

    def has_module_perms(self, app_label):
      "Does the user have permissions to view the app `app_label`?"
      # Simplest possible answer: Yes, always
      return self.is_admin or self.is_superuser

    @property
    def is_staff(self):
      "Is the user a member of staff?"
      # Simplest possible answer: All admins are staff
      return self.is_admin
