from django.db import models
from accounts.models import Account,DealerProfile
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from rest_framework_simplejwt.tokens import RefreshToken
# Create your models here.

class EmployeeManager(BaseUserManager):

    def create_Employee(self, username, email, mobile_number,aadhar_card,auth_id=None,dealer_id=None,dealer_email=None,ProfilePic=None, password = None):
        if username is None:
            raise TypeError('Employee should have a Username')
        if email is None:
            raise TypeError('Employee should have an Email Id')
        if mobile_number is None:
            raise TypeError('Employee should have a Mobile Number')
        if aadhar_card is None:
            raise TypeError('Employee should have an aadhar_card')
        if dealer_email is None:
            raise TypeError('Employee you should enter an dealer_email')
        if ProfilePic is None:
            ProfilePic = "photos/Profile_Pic.png"

        employee = self.model(auth_id=auth_id,dealer_id=dealer_id,username = username, email = self.normalize_email(email), ProfilePic=ProfilePic, mobile_number = mobile_number, aadhar_card = aadhar_card,)
        employee.set_password(password)
        employee.save(using = self._db)
        return employee


class Employee(AbstractBaseUser):
    auth_id= models.OneToOneField(Account,on_delete=models.CASCADE,null=True)
    dealer_id = models.ForeignKey(DealerProfile,on_delete=models.SET_NULL,null=True,blank = True)
    username = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    kt_id = models.CharField(max_length=50,default="KTDE")
    mobile_number = models.CharField(max_length=12)
    aadhar_card = models.FileField(upload_to='accounts/Employee/aadhar_cards')
    qrCode = models.ImageField(default = 'cvm_qrcodes/4.jpg', upload_to='accounts/Employee/QRs')
    ProfilePic = models.ImageField(default = 'photos/Profile_Pic.png', upload_to='accounts/Employee/ProfilePic', null = True, blank = True)
    # pass_code = models.CharField(max_length=6, default = '000000', null = True, blank = True)
    id_card =  models.ImageField(upload_to='accounts/Employee/id_cards',null = True, blank = True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    online = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'mobile_number' ,'aadhar_card',]

    objects = EmployeeManager()

    def __str__(self):
        return str(self.id)
    
    def has_perm(self, perm, obj = None):
        return self.is_admin

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

from django.db.models.signals import post_delete,pre_delete
from django.dispatch import receiver

@receiver(post_delete, sender=Employee)
def delete_employee_related_user(sender,instance, **kwargs):
    try:
        instance.auth_id.delete()
    except:
        pass