"""
URL configuration for ufcapi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.models import User
from ufcapi import settings
from ufcscraper.filters import FightFilter
from ufcscraper.models import Event, Fighter, Fight
from django.urls import path, include
from django.db.models import Q

from rest_framework import routers, serializers, viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework_api_key.permissions import HasAPIKey
from django_filters.rest_framework import DjangoFilterBackend


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "is_staff"]


class EventSerializer(serializers.HyperlinkedModelSerializer):
    details = serializers.HyperlinkedIdentityField(view_name="event-detail")

    class Meta:
        model = Event
        fields = [
            "id",
            "details",
            "location",
            "date",
            "upcoming",
            "link",
            "event_id",
            "name",
            "type",
            "completed",
        ]


class FighterSerializer(serializers.HyperlinkedModelSerializer):
    details = serializers.HyperlinkedIdentityField(view_name="fighter-detail")

    class Meta:
        model = Fighter
        fields = [
            "id",
            "details",
            "link",
            "fighter_id",
            "photo_url",
            "first_name",
            "last_name",
            "nickname",
            "height",
            "weight",
            "reach",
            "stance",
            "belt",
            "win",
            "loss",
            "draw",
        ]


class FightSerializer(serializers.HyperlinkedModelSerializer):
    details = serializers.HyperlinkedIdentityField(view_name="fight-detail")
    fighter_one = serializers.PrimaryKeyRelatedField(queryset=Fighter.objects.all())
    fighter_two = serializers.PrimaryKeyRelatedField(queryset=Fighter.objects.all())
    winner = serializers.PrimaryKeyRelatedField(
        queryset=Fighter.objects.all(), allow_null=True
    )
    fighter_one_detail = FighterSerializer(source="fighter_one", read_only=True)
    fighter_two_detail = FighterSerializer(source="fighter_two", read_only=True)

    class Meta:
        model = Fight
        fields = [
            "id",
            "details",
            "fight_id",
            "position",
            "weight_class",
            "fighter_one",
            "fighter_two",
            "fighter_one_detail",
            "fighter_two_detail",
            "method",
            "round",
            "time",
            "event",
            "belt",
            "bonus",
            "wl_fighter_one",
            "wl_fighter_two",
            "winner",
        ]


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by("-date")
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["upcoming", "completed", "type", "event_id"]
    search_fields = ["name", "location"]
    permission_classes = [HasAPIKey | IsAuthenticatedOrReadOnly]


class FighterViewSet(viewsets.ModelViewSet):
    queryset = Fighter.objects.all()
    serializer_class = FighterSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["weight", "stance", "belt", "fighter_id"]
    search_fields = ["first_name", "last_name", "nickname", "fighter_id"]
    permission_classes = [HasAPIKey | IsAuthenticatedOrReadOnly]


class FightViewSet(viewsets.ModelViewSet):
    queryset = Fight.objects.all()
    ordering = [
        "event__date",
        "position",
    ]
    ordering_fields = [
        "event__date",
        "position",
    ]
    serializer_class = FightSerializer
    filterset_class = FightFilter
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    permission_classes = [HasAPIKey | IsAuthenticatedOrReadOnly]


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r"events", EventViewSet)
router.register(r"fighters", FighterViewSet)
router.register(r"fights", FightViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("redegg.urls")),
    path("__reload__/", include("django_browser_reload.urls")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
