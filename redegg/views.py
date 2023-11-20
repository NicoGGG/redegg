from itertools import zip_longest
from django.shortcuts import get_object_or_404, render, redirect

from redegg.models import Contest, Prediction
from redegg.forms import PrognosticForm
from ufcscraper.models import Fight


def home(request):
    latest_contest = Contest.objects.order_by("-event__date").first()
    return redirect("create_prediction", contest_id=latest_contest.id)


def create_prediction(request, contest_id):
    contest = get_object_or_404(Contest, pk=contest_id)
    fights = Fight.objects.filter(event=contest.event).order_by("position")

    if request.user.is_authenticated:
        prediction = Prediction.objects.filter(
            user=request.user, contest=contest
        ).first()
        if prediction:
            prognostics = prediction.prognostic_set.all()
        else:
            prognostics = [None] * len(fights)
    else:
        prediction = None
        prognostics = [None] * len(fights)

    if contest.status == "open" and request.method in ["POST", "PUT"]:
        forms = [
            PrognosticForm(
                request.POST, prefix=str(fight.id), fight=fight, instance=prognostic
            )
            for fight, prognostic in zip_longest(fights, prognostics, fillvalue=None)
        ]
        if all(form.is_valid() for form in forms):
            if not prediction:
                prediction = Prediction.objects.create(
                    user=request.user, contest=contest
                )
            for form, fight in zip(forms, fights):
                if form.cleaned_data.get("fight_result") or form.cleaned_data.get(
                    "is_draw"
                ):
                    prognostic = form.save(commit=False)
                    prognostic.prediction = prediction
                    prognostic.fight = fight  # Set the fight
                    prognostic.save()
        else:
            for form in forms:
                if not form.is_valid():
                    print(form.errors)
    else:
        forms = [
            PrognosticForm(prefix=str(fight.id), fight=fight, instance=prognostic)
            for fight, prognostic in zip_longest(fights, prognostics, fillvalue=None)
        ]
    prognostic_dict = {
        prognostic.fight.id: prognostic
        for prognostic in prognostics
        if prognostic is not None
    }
    fight_prognostic_pairs = [
        (fight, prognostic_dict.get(fight.id)) for fight in fights
    ]
    context = {
        "contest_name": str(contest),
        "contest_date": contest.event.date,
        "contest": contest,
        "fight_prognostic_pairs": fight_prognostic_pairs,
        "fights": fights,
        "prognostics": prognostics,
        "prediction": prediction,
        "forms": forms,
    }
    if contest.status in ["live", "closed"]:
        # If the contest is live or closed, just display the fights without a form
        return render(request, "view_prediction.html", context)
    return render(request, "create_prediction.html", context)
