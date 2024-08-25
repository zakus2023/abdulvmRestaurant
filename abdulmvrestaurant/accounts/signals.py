from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import UserProfile, User

#creating the django signal receiver
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


# This will be triggerred just before the user is saved
@receiver(pre_save, sender=User)
def pre_save_create_profile_receiver(sender, instance, **kwargs):
    print("This user is being saved")