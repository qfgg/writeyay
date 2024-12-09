import os
# import boto3
# from botocore.exceptions import ClientError
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
# from django.contrib.auth.views import PasswordResetView
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages
from .forms import RegistrationForm, LoginForm
DOMAIN = os.getenv('REDIRECT_DOMAIN')
# aws ses email
# AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')


# class CustomPasswordResetView(PasswordResetView):
#     def send_mail(self, subject, message, from_email, recipient_list, **kwargs):
#         from_email = 'joo@writeyay.com'
#         ses_client = boto3.client(
#             'ses',
#             aws_access_key_id=AWS_ACCESS_KEY_ID,
#             aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
#             region_name='us-east-2'
#         )
#         try:
#             ses_client.send_email(
#                 Source=from_email,
#                 Destination={
#                     'ToAddresses': recipient_list,
#                 },
#                 Message={
#                     'Subject': {
#                         'Data': subject,
#                         'Charset': 'UTF-8'
#                     },
#                     'Body': {
#                         'Text': {
#                             'Data': message,
#                             'Charset': 'UTF-8'
#                         },
#                     },
#                 }
#             )
#         except ClientError as e:
#             print(e.response['Error']['Message'])


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            user = User.objects.create_user(username=email, email=email, password=password, is_active=False)
            user.save()

            # ses_client = boto3.client(
            #     'ses',
            #     aws_access_key_id=AWS_ACCESS_KEY_ID,
            #     aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            #     region_name='us-east-2'
            # )
            mail_subject = '[WRITEYAY] Activate your account.'
            message = render_to_string('accounts/activation_email.html', {
                'user': user,
                'domain': DOMAIN,
                'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            send_mail(mail_subject, message, settings.EMAIL_HOST_USER, [email])
            # try:
            #     ses_client.send_email(
            #         Source='joo@writeyay.com',
            #         Destination={
            #             'ToAddresses': [email],
            #         },
            #         Message={
            #             'Subject': {
            #                 'Data': mail_subject,
            #                 'Charset': 'UTF-8'
            #             },
            #             'Body': {
            #                 'Text': {
            #                     'Data': message,
            #                     'Charset': 'UTF-8'
            #                 },
            #             },
            #         }
            #     )
            # except ClientError as e:
            #     print(e.response['Error']['Message'])
            return redirect('verify')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def verify(request):
    return render(request, 'accounts/email_verification.html')

def activate(request, uidb64, token):
    UserModel = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UserModel.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid!')
        return redirect('register')

def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, "Invalid email or password.")
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')

def login_cancelled(request):
    return redirect('login')

def sociallogin_local_exist_success(request):
    return redirect('home')
