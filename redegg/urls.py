from django.urls import path
from django.contrib.auth import views as auth_views
from redegg.views import (
    ContestLeaderboard,
    ContestListView,
    PredictionDetailView,
    PredictionListView,
    create_prediction,
    home,
)

urlpatterns = [
    path("", home, name="home"),
    path(
        "login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    path("account/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("contests/", ContestListView.as_view(), name="contest_list"),
    path(
        "contest/<slug:contest_slug>/",
        create_prediction,
        name="create_prediction",
    ),
    path(
        "contest/<slug:contest_slug>/leaderboard/",
        ContestLeaderboard.as_view(),
        name="contest_leaderboard",
    ),
    path("predictions/", PredictionListView.as_view(), name="prediction_list"),
    path(
        "prediction/<str:prediction_id>/",
        PredictionDetailView.as_view(),
        name="prediction_detail",
    ),
]
