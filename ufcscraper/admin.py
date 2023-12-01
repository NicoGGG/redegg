from django import forms
from django.contrib import admin
from ufcscraper.tasks import scrape_ufc_event_fights
from ufcscraper.utils import create_or_update_contest
from .models import Fighter, Event, Fight


class EventAdmin(admin.ModelAdmin):
    actions = ["create_update_contest", "scrape_event_fights"]
    ordering = ["-date"]

    def create_update_contest(self, request, queryset):
        for event in queryset:
            create_or_update_contest(str(event.event_id))
        self.message_user(
            request, "Contests created/updated successfully for selected events"
        )

    create_update_contest.short_description = (
        "Create or update related contests for selected events"
    )

    def scrape_event_fights(self, request, queryset):
        for event in queryset:
            scrape_ufc_event_fights.apply_async(args=[str(event.event_id)])
        self.message_user(request, "Fights scraped successfully for selected events")

    scrape_event_fights.short_description = "Scrape fights for selected events"


class FightForm(forms.ModelForm):
    class Meta:
        model = Fight
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance")
        if instance:
            self.fields["winner"].choices = [
                (None, "---------"),
                (instance.fighter_one.id, str(instance.fighter_one)),
                (instance.fighter_two.id, str(instance.fighter_two)),
            ]


class FightAdmin(admin.ModelAdmin):
    form = FightForm
    list_filter = ("event",)
    ordering = ["-event__date", "position"]


class FighterAdmin(admin.ModelAdmin):
    ordering = ["last_name"]
    readonly_fields = ["fighter_id", "link"]
    list_display = ["first_name", "last_name", "nickname", "weight", "belt"]
    list_filter = ["belt", "weight"]


admin.site.register(Event, EventAdmin)
admin.site.register(Fight, FightAdmin)
admin.site.register(Fighter, FighterAdmin)
