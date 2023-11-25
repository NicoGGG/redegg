from django.urls import path
from redegg.views import (
    ContestListView,
    PredictionDetailView,
    PredictionListView,
    create_prediction,
    home,
)

urlpatterns = [
    path("", home, name="home"),
    # Dummy login and logout views
    path("login/", lambda request: None, name="login"),
    path("logout/", lambda request: None, name="logout"),
    path("contests/", ContestListView.as_view(), name="contest_list"),
    path(
        "contest/<slug:contest_slug>/",
        create_prediction,
        name="create_prediction",
    ),
    path("predictions/", PredictionListView.as_view(), name="prediction_list"),
    path(
        "prediction/<str:prediction_id>/",
        PredictionDetailView.as_view(),
        name="prediction_detail",
    ),
]
