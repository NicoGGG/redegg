from django.contrib import admin
from django.db.models import Q

from ufcscraper.models import Fight, Fighter

# Register your models here.

from .models import Contest, Prediction, Prognostic


class PrognosticAdmin(admin.ModelAdmin):
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


admin.site.register(Contest)
admin.site.register(Prediction)
admin.site.register(Prognostic, PrognosticAdmin)
