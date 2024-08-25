from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.conf import settings

#this will be used to redirect the user to a specific dashboard based on the user role
def detectUser(user):
    if user.role == 1:
        redirectUrl = 'vendorDashboard'
        return redirectUrl
    
    elif user.role == 2:
        redirectUrl = 'custdashboard'
        return redirectUrl
    
    elif user.role == None and user.is_superadmin:
        redirectUrl = '/admin'
        return redirectUrl
    

# this will be used to send verification email

def send_verification_email(request, user, mail_subject, email_template):
    from_email = settings.DEFAULT_FROM_EMAIL
    current_site = get_current_site(request)
    message = render_to_string(email_template, {
        'user': user, 
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
    })

    to_email = user.email
    mail = EmailMessage(mail_subject, message, from_email, to=[to_email])

    # in order to send the email as html template you must addthe following. after adding this go to the email templates
    mail.content_subtype='html'
    # -----------------------------------

    mail.send()


#this function will send the password reset email to the user

# def send_password_reset_email(request, user):
#     from_email = settings.DEFAULT_FROM_EMAIL
#     current_site = get_current_site(request)
#     mail_subject = 'Reset your password'
#     message = render_to_string('accounts/emails/reset_password_email.html', {
#         'user': user, 
#         'domain': current_site,
#         'uid': urlsafe_base64_encode(force_bytes(user.pk)),
#         'token': default_token_generator.make_token(user),
#     })

#     to_email = user.email
#     mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
#     mail.send()

#this function is going to handle sending notification to user when the vendor is approved or otherwise
def send_notification(mail_subject, mail_template, context):
    from_email = settings.DEFAULT_FROM_EMAIL
    message = render_to_string(mail_template, context)

    # check if the to email is not a list
    if(isinstance(context['to_email'], str)):
        # initialize a list
        to_email = []
        # add the to email to a list email to the list
        to_email.append(context['to_email'])
    else:
        # otherwise the to email is a list is a list
        to_email = context['to_email']
    mail = EmailMessage(mail_subject, message, from_email, to=to_email)
    # in order to send the email as html template you must addthe following. 
    # after adding this go to the views where we send the emails
    mail.content_subtype='html'
    mail.send()

    
        