from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
# from django.db.models.signals import post_save, pre_save
# from django.dispatch import receiver

from . validators import allow_only_images_validator

from django.contrib.gis.db import models as gismodels
from django.contrib.gis.geos import Point

# Create your models here.

class UserManager(BaseUserManager):
    #creating the regular user
    def create_user(self, first_name, last_name, username, email, phone_number, password=None):
        if not email:
            raise ValueError('User must have email address')
        if not username:
            raise ValueError('User must have a useename')
        
        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
            phone_number=phone_number,
            
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    #creating the super user
    def create_superuser(self, first_name, last_name, username, email, password=None):
        user = self.create_user(
            email = self.normalize_email(email),
            password = password,
            username = username,
            first_name = first_name,
            last_name = last_name,
        )

        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    VENDOR = 1
    CUSTOMER = 2

    ROLE_CHOICE = (
        (VENDOR, 'Vendor'),
        (CUSTOMER, 'Customer'),
    )

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=12, blank=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICE, blank=True, null=True)

    #required fields

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_data = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    #authentication part: sing the email instaed of the username to authenticate the user. By default django uses the username

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True
    
    #use this to get the role of a user and use it to direct user to appropriate dashboard
    def get_role(self):
        if self.role == 1:
            user_role = 'Vendor'
        else:
            user_role = 'Customer'

        return user_role
    


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='users/profile_picture', blank=True, null=True)
    cover_photo = models.ImageField(upload_to='users/cover_photo', blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    # address_line_1 = models.CharField(max_length=255, blank=True, null=True)
    # address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    province = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.CharField(max_length=100, blank=True, null=True)
    longitude = models.CharField(max_length=100, blank=True, null=True)
    # srid: spatial refernce identifier. by default it is 4326
    location = gismodels.PointField(blank=True, null=True, srid=4326)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email
    # overwriting the svae method of the UserProfile model
    def save(self, *args, **kwargs):
        # check if latitude and longitude exist
        if self.latitude and self.longitude:
            # create the point. NB: whenever you create a point the first parameter should be longitude, then latitude
            # make sure you convert the lat and lng to float
            self.location = Point(float(self.longitude), float(self.latitude))
            # overwrite the save method
            return super(UserProfile, self).save(*args, **kwargs)
        # so that if the lng and lat do not exist the object will still be saved
        return super(UserProfile, self).save(*args, **kwargs)

    

    # i commented this when i changed the addree 1 and addre 2 to only address
    
    # def full_address(self):
    #     return f'{self.address_line_1}, {self.address_line_2}, {self.city}, {self.province}, {self.country}, {self.postal_code}'
    


    # #creating the django signal receiver
    # @receiver(post_save, sender=User)
    # def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    #     #print(created)
    #     if created:
    #         #print('Create the user profile'). This cretaes the profile when the user is first created
    #         UserProfile.objects.create(user=instance)
    #     else:
    #         try:
    #             #print("User is updated"). This saves the profile when the user is updated
    #             profile = UserProfile.objects.get(user=instance)
    #             profile.save()
    #         except:
    #             #create the profile if not exist. This is when the user is updated but the profile does not exist
    #             UserProfile.objects.create(user=instance)
    #             print("User recreated")


    # # This will be triggerred just before the user is saved
    # @receiver(pre_save, sender=User)
    # def pre_save_create_profile_receiver(sender, instance, **kwargs):
    #     print("This user is being saved")



    #one way to connect the receiver to the sender. The sender here is the User model
    #post_save.connect(post_save_create_profile_receiver,sender=User)