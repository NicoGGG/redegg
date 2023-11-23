from django.urls import path
from .views import create_prediction, home

urlpatterns = [
    path("", home, name="home"),
    # Dummy login and logout views
    path("login/", lambda request: None, name="login"),
    path("logout/", lambda request: None, name="logout"),
    path(
        "contest/<slug:contest_slug>/",
        create_prediction,
        name="create_prediction",
    ),
    # ...
]
