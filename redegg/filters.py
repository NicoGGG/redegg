# filters.py
import django_filters
from redegg.models import Prediction
from redegg.forms import SocialAccountForm


class PredictionFilter(django_filters.FilterSet):
    user__socialaccount__provider = django_filters.ChoiceFilter(
        choices=SocialAccountForm.PROVIDERS
    )
    user__profile__display_username = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Prediction
        fields = [
            "user__socialaccount__provider",
            "user__profile__display_username",
        ]
        form = SocialAccountForm
