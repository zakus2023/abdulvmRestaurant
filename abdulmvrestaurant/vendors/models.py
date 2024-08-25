from django.db import models
from accounts.models import User, UserProfile
from accounts.utils import send_notification

from datetime import time, datetime, date

# Create your models here.

class Vendor(models.Model):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='userprofile', on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=255)
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_license = models.ImageField(upload_to='vendor/license')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.vendor_name
    
    # this is a member function to hold the current opening hour
    # I will use it to display whether the vendor is open or closed on the home page
    
    def is_open(self):
        todays_date = date.today()
        # get the day of the weeks number
        today = todays_date.isoweekday()
        # filter the opening hours with the self(self is the model itself) and day of the week and pass it as contect dictionary 
        current_days_opening_hours = OpeningHours.objects.filter(vendor=self, day=today)

         # get the current time
        now = datetime.now()
        # convert the the current time to string and set the format to 24h
        current_time = now.strftime("%H:%M:%S")

        # loop through the currenet_opening_hours and check if the current time falls within it
         # there was a roblem with this member function.
        # the problem it was causing was when a vendor is closed for a particular day it throws an error when you try to
        # diplay whether it is opened or closed. I solved it by adding if i.is_closed: is_open = False in the for loop
        is_open = None
        for i in current_days_opening_hours:
            if i.is_closed:
                 is_open = False
                 break
            # set the opening time to compare with. That should be the from_hour. Then convert it to the required format
            # the conversion should be as it was converted to be stored in the db. ,time() will get you only the time
            # str(datetime...) this will convert it to str. strptime will string format it.
            opening_time = str(datetime.strptime(i.from_hour, "%I:%M %p").time())
            # get the closing time compare with. That should be the from_hour. Then convert it to the required format
            closing_time = str(datetime.strptime(i.to_hour, "%I:%M %p").time())

            # check if the current time is within the opening and closing time
            if current_time > opening_time and current_time < closing_time:
                is_open = True
                break
            else:
                is_open = False
        # whenever you want to know whether the vendor is opened or closed use vendor.is_open. 
        # it will return true or false based on the above function
        return is_open

       

    # def is_open(self):
    #     todays_date = date.today()
    #     today = todays_date.isoweekday()
    #     current_days_opening_hours = OpeningHours.objects.filter(vendor=self, day=today)

    #     now = datetime.now()
    #     current_time = now.strftime("%H:%M:%S")

    #     is_open = False  # Default to False

    #     for i in current_days_opening_hours:
    #         if i.is_closed:
    #             is_open = False
                
    #         else:
    #             opening_time = str(datetime.strptime(i.from_hour, "%H:%M %p").time())
    #             closing_time = str(datetime.strptime(i.to_hour, "%H:%M %p").time())

    #             # if opening_time <= current_time <= closing_time:
    #             #     is_open = True
    #             #     break

    #             if current_time > opening_time and current_time < closing_time:
    #                 is_open = True
    #                 break
    #             else:
    #                  is_open = False

    #     return is_open
    

    # -------------------------------------------------------
    def save(self, *args, **kwargs):
        # check if the vendor is created already or exist
        if self.pk is not None:
            #update it
            orig = Vendor.objects.get(pk=self.pk)
            if orig.is_approved != self.is_approved:

                mail_template = 'accounts/emails/admin_approval_email.html'
                context = {
                    'user':self.user,
                    'is_approved': self.is_approved,
                    'to_email': self.user.email
                }
                if self.is_approved == True:
                    #Send approval email
                    mail_subject = "Application approved"                    
                    send_notification(mail_subject, mail_template, context)
                else:
                    # send non approval email
                    mail_subject = "Application rejected"
                    send_notification(mail_subject, mail_template, context)


        #the super function allows you to access the save method of the vendor class
        return super(Vendor, self).save(*args, **kwargs)
    


# opening hours model
DAYS = [
    (1, ('Monday')),
    (2, ('Tuesday')),
    (3, ('Wednesday')),
    (4, ('Thursday')),
    (5, ('Friday')),
    (6, ('Saturday')),
    (7, ('Sunday')),
]

HOUR_OF_DAY_24 = [((time(h, m).strftime('%I:%M %p')),(time(h, m).strftime('%I:%M %p'))) for h in range(0, 24) for m in (0, 30)]

class OpeningHours(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='opening_hours')
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(choices=HOUR_OF_DAY_24, max_length=10, blank=True)
    to_hour = models.CharField(choices=HOUR_OF_DAY_24, max_length=10, blank=True)
    is_closed = models.BooleanField(default=False)


    def __str__(self):
        # use self.get_day_display() this will give you the days instead of the numbers in the choices
        return self.get_day_display()

    class Meta:
        ordering = ('day', '-from_hour')
        # this will prevent adding the same times for the same day.
        # it will check if the vendor is the same and the day is the same and the from and to hour is the same
        unique_together = ('vendor','day', 'from_hour', 'to_hour')

    