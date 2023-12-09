from django.dispatch import receiver
from redegg.models import UserProfile
from ufcscraper.utils import send_discord_notification
from allauth.socialaccount.signals import (
    social_account_updated,
)
from allauth.account.signals import user_signed_up

from ufcscraper.utils import send_discord_notification


@receiver(user_signed_up)
@send_discord_notification
def handle_user_signup(sender, request, user, sociallogin, **kwargs):
    # This code will be executed after a user signs up via a social provider,
    UserProfile.objects.create(user=sociallogin.user)
    sociallogin.user.refresh_from_db()  # Refresh the User instance from the database
    if sociallogin.account.provider == "twitter_oauth2":
        sociallogin.user.profile.display_username = (
            "@" + sociallogin.account.extra_data["username"]
        )
        sociallogin.user.profile.avatar_url = sociallogin.account.extra_data[
            "profile_image_url"
        ]
    if sociallogin.account.provider == "reddit":
        sociallogin.user.profile.display_username = (
            "u/" + sociallogin.account.extra_data["name"]
        )
        sociallogin.user.profile.avatar_url = sociallogin.account.extra_data["icon_img"]
    sociallogin.user.profile.extra_data = sociallogin.account.extra_data
    sociallogin.user.profile.save()
    message = f"User signed up: {sociallogin.user.username} - {sociallogin.user.id} from {sociallogin.account.provider}"
    print(message)
    return message


@receiver(social_account_updated)
def handle_social_login(sender, request, sociallogin, **kwargs):
    if sociallogin.account.provider == "twitter_oauth2":
        sociallogin.user.profile.display_username = (
            "@" + sociallogin.account.extra_data["username"]
        )
        sociallogin.user.profile.avatar_url = sociallogin.account.extra_data[
            "profile_image_url"
        ]
    if sociallogin.account.provider == "reddit":
        sociallogin.user.profile.display_username = (
            "u/" + sociallogin.account.extra_data["name"]
        )
        sociallogin.user.profile.avatar_url = sociallogin.account.extra_data["icon_img"]
    sociallogin.user.profile.extra_data = sociallogin.account.extra_data
    sociallogin.user.profile.save()
