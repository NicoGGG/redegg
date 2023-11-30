from django.contrib import admin
from django.db.models import Q
from django.core.management import call_command

from ufcscraper.models import Fight, Fighter

from .models import Contest, Prediction, UserProfile, Prognostic


class ContestAdmin(admin.ModelAdmin):
    actions = ["calculate_scores"]
    ordering = ["-event__date"]

    def calculate_scores(self, request, queryset):
        for contest in queryset:
            call_command("calculate_prognostics_score", str(contest.id))
        self.message_user(request, "Scores calculated successfully")

    calculate_scores.short_description = "Calculate scores for selected contests"


class PredictionAdmin(admin.ModelAdmin):
    readonly_fields = ["prediction_id"]


class PrognosticAdmin(admin.ModelAdmin):
    actions = ["reset_prognostic_result"]
    list_filter = ("prediction__contest__event", "prediction__user")
    ordering = ["-prediction__contest__event__date", "fight__position"]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        prognostic_id = request.resolver_match.kwargs.get("object_id")
        if prognostic_id:
            prognostic = Prognostic.objects.get(id=prognostic_id)
            fight = prognostic.fight
        else:
            fight = None

        if db_field.name == "fight":
            kwargs["queryset"] = Fight.objects.filter(
                event__contest__prediction__prognostic__id=prognostic_id
            )
        if db_field.name == "fight_result" and fight:
            kwargs["queryset"] = Fighter.objects.filter(
                Q(id=fight.fighter_one.id) | Q(id=fight.fighter_two.id)
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def reset_prognostic_result(self, request, queryset):
        for prognostic in queryset:
            prognostic.fight_result_won = False
            prognostic.points = 0
            prognostic.bonus_percentage = 0
            prognostic.method_won = False
            prognostic.bonus_won = False
            prognostic.save()
        self.message_user(request, "Prognostic results reset successfully")

    reset_prognostic_result.short_description = "Reset prognostic results and score"


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["display_username"]


admin.site.register(Contest, ContestAdmin)
admin.site.register(Prediction, PredictionAdmin)
admin.site.register(Prognostic, PrognosticAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
