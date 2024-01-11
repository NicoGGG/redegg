from django.dispatch import receiver
from django.db.models.signals import pre_save
from allauth.socialaccount.signals import (
    social_account_updated,
)
from allauth.account.signals import user_signed_up

from ufcscraper.utils import send_discord_notification

from redegg.models import UserProfile, Contest
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
        sociallogin.user.profile.base_username = sociallogin.account.extra_data[
            "username"
        ]
    if sociallogin.account.provider == "reddit":
        sociallogin.user.profile.display_username = (
            "u/" + sociallogin.account.extra_data["name"]
        )
        sociallogin.user.profile.avatar_url = sociallogin.account.extra_data[
            "icon_img"
        ].replace("amp;", "")
        sociallogin.user.profile.base_username = sociallogin.account.extra_data["name"]
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
        sociallogin.user.profile.avatar_url = sociallogin.account.extra_data[
            "icon_img"
        ].replace("amp;", "")
    sociallogin.user.profile.extra_data = sociallogin.account.extra_data
    sociallogin.user.profile.save()


@receiver(pre_save, sender=Contest)
def calculate_predictions_ranks(sender, instance: Contest, **kwargs):
    try:
        # Get the old instance from the database
        old_instance = Contest.objects.get(pk=instance.pk)
    except Contest.DoesNotExist:
        # The instance is not in the database (probably it's being created)
        return
    if not old_instance.status == "closed" and instance.status == "closed":
        # Calculate points for the last time when the contest is closed
        for prediction in instance.prediction_set.all():
            prediction.calculate_points()
            prediction.save()
        # Calculate ranks
        instance.calculate_all_predictions_rank()
        message = f"Calculating ranks for contest {instance} - {instance.pk}"
        print(message)
        return message
