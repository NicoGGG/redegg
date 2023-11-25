from django.contrib import admin
from .models import Fighter, Event, Fight
from django.core.management import call_command


class EventAdmin(admin.ModelAdmin):
    actions = ["create_update_contest", "scrape_fighters"]
    ordering = ["-date"]

    def create_update_contest(self, request, queryset):
        for event in queryset:
            call_command("create_update_contest", str(event.event_id))
        self.message_user(
            request, "Contests created/updated successfully for selected events"
        )

    create_update_contest.short_description = (
        "Create or update related contests for selected events"
    )

    def scrape_fighters(self, request, queryset):
        for event in queryset:
            call_command("scrape_ufc_event_fights", str(event.event_id))
        self.message_user(request, "Fighters scraped successfully for selected events")

    scrape_fighters.short_description = "Scrape fighters for selected events"


class FightAdmin(admin.ModelAdmin):
    ordering = ["-event__date", "position"]


admin.site.register(Fighter)
admin.site.register(Event, EventAdmin)
admin.site.register(Fight, FightAdmin)
