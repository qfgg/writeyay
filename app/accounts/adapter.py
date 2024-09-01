from django.contrib.auth.models import User
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import complete_signup


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # get sociallogin email
        email = sociallogin.account.extra_data.get('email')

        # check if exists in local User
        if email:
            try:
                user = User.objects.get(email=email)

                # if user found, go on loginning
                if user:
                    # set as current user
                    sociallogin.user = user
                    sociallogin.email_addresses = [email]
                    sociallogin.state['process'] = 'connect'
                    # not sure why success_url never works, workaround overwrite view of 'auth/3rdparty/'
                    complete_signup(request, user, 'socialaccount', success_url='/')

            except User.DoesNotExist:
                pass
