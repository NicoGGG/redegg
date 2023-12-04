from allauth.socialaccount import providers
from importlib import import_module
from django.urls import path
from django.views.generic.base import RedirectView
from allauth.account import views as accountviews
from allauth.socialaccount import views as socialaccountviews

urlpatterns = [
    path("login/", accountviews.login, name="account_login"),
    path("logout/", accountviews.logout, name="account_logout"),
    path(
        "signup/",
        RedirectView.as_view(url="/accounts/login/", permanent=True),
        name="account_signup",
    ),
    path(
        "login/cancelled/",
        socialaccountviews.login_cancelled,
        name="socialaccount_login_cancelled",
    ),
    path(
        "login/error/",
        socialaccountviews.login_error,
        name="socialaccount_login_error",
    ),
]

# Provider urlpatterns, as separate attribute (for reusability).
provider_urlpatterns = []
provider_classes = providers.registry.get_class_list()

# We need to move the OpenID Connect provider to the end. The reason is that
# matches URLs that the builtin providers also match.
provider_classes = [cls for cls in provider_classes if cls.id != "openid_connect"] + [
    cls for cls in provider_classes if cls.id == "openid_connect"
]
for provider_class in provider_classes:
    try:
        prov_mod = import_module(provider_class.get_package() + ".urls")
    except ImportError:
        continue
    prov_urlpatterns = getattr(prov_mod, "urlpatterns", None)
    if prov_urlpatterns:
        provider_urlpatterns += prov_urlpatterns

urlpatterns += provider_urlpatterns
