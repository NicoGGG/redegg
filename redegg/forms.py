from django import forms
from django.forms import formset_factory

from ufcscraper.models import Fight, Fighter
from redegg.models import Prognostic


class AriaLabelRadioSelect(forms.RadioSelect):
    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        option_dict = super().create_option(
            name, value, label, selected, index, subindex=subindex, attrs=attrs
        )
        option_dict["attrs"]["aria-label"] = label
        return option_dict


class PrognosticForm(forms.ModelForm):
    fight = forms.ModelChoiceField(queryset=Fight.objects.none(), required=False)
    fight_result = forms.ChoiceField(choices=[], required=False)
    method = forms.ChoiceField(
        choices=Prognostic.METHOD_CHOICES,
        widget=AriaLabelRadioSelect(
            attrs={"class": "join-item btn method-field"},
        ),
        required=False,
    )
    bonus = forms.ChoiceField(
        choices=Prognostic.BONUS_CHOICES,
        widget=AriaLabelRadioSelect(
            attrs={"class": "join-item btn bonus-field"},
        ),
        required=False,
    )

    class Meta:
        model = Prognostic
        fields = ["fight_result", "is_draw", "method", "bonus"]

    def __init__(self, *args, **kwargs):
        self.fight = kwargs.pop("fight", None)
        super().__init__(*args, **kwargs)
        if self.fight:
            self.fields["fight_result"].choices = [
                (None, "---------"),
                (self.fight.fighter_one.id, str(self.fight.fighter_one)),
                (self.fight.fighter_two.id, str(self.fight.fighter_two)),
            ]

    def clean_fight_result(self):
        fight_result_id = self.cleaned_data.get("fight_result")
        if fight_result_id and fight_result_id != "None":
            try:
                return Fighter.objects.get(id=fight_result_id)
            except Fighter.DoesNotExist:
                raise forms.ValidationError("Fighter with given ID does not exist")
        return None

    def get_fighter_details(self, fighter):
        # Return detailed information about a fighter
        return {
            "id": fighter.id,
            "name": fighter.first_name + " " + fighter.last_name,
            "photo_url": fighter.photo_url,
            "record": fighter.record(),
            # Include other details as needed
        }

    @property
    def fighter_one_details(self):
        return self.get_fighter_details(self.fight.fighter_one)

    @property
    def fighter_two_details(self):
        return self.get_fighter_details(self.fight.fighter_two)

    @property
    def fight_id(self):
        return self.fight.id if self.fight else None

    @property
    def fight_info(self):
        out = str(self.fight) + ": " + self.fight.weight_class + " "
        out += "Title Fight" if self.fight.belt else "Bout"
        return out

    @property
    def fight_position(self):
        if self.fight.position == 1:
            out = "Main Event"
        elif self.fight.position == 2:
            out = "Co-Main Event"
        elif self.fight.position in range(3, 6):
            out = "Main Card"
        else:
            out = "Prelim"
        return out

    @property
    def fight_card_position(self):
        if self.fight.position == 1:
            out = "main-event"
        elif self.fight.position == 2:
            out = "co-main-event"
        elif self.fight.position in range(3, 6):
            out = "main-card"
        else:
            out = "prelim"
        return out

    @property
    def is_title_fight(self):
        return self.fight.belt


PrognosticFormSet = formset_factory(PrognosticForm, extra=1)
