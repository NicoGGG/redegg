from itertools import zip_longest
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator

from redegg.models import Contest, Prediction
from redegg.forms import PrognosticForm
from ufcscraper.models import Fight


def home(request):
    latest_contest = Contest.objects.order_by("-event__date").first()
    return redirect("create_prediction", contest_slug=latest_contest.slug)


def create_prediction(request, contest_slug):
    contest = get_object_or_404(Contest, slug=contest_slug)
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

    prognostic_dict = {
        prognostic.fight.id: prognostic
        for prognostic in prognostics
        if prognostic is not None
    }
    fight_prognostic_pairs = [
        (fight, prognostic_dict.get(fight.id)) for fight in fights
    ]

    if contest.status == "open" and request.method in ["POST", "PUT"]:
        forms = [
            PrognosticForm(
                request.POST, prefix=str(fight.id), fight=fight, instance=prognostic
            )
            for fight, prognostic in fight_prognostic_pairs
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
            return redirect("prediction_detail", prediction_id=prediction.prediction_id)
        else:
            for form in forms:
                if not form.is_valid():
                    print(form.errors)
    else:
        forms = [
            PrognosticForm(prefix=str(fight.id), fight=fight, instance=prognostic)
            for fight, prognostic in fight_prognostic_pairs
        ]

    context = {
        "contest_name": str(contest),
        "contest_date": contest.event.date,
        "contest": contest,
        "prediction": prediction,
        "fight_prognostic_pairs": fight_prognostic_pairs,
        "forms": forms,
    }
    if contest.status in ["live", "closed"]:
        # If the contest is live or closed, just display the fights without a form
        return render(request, "view_prediction.html", context)
    return render(request, "create_prediction.html", context)


class ContestListView(ListView):
    model = Contest
    template_name = "contest_list.html"  # Replace with your template
    context_object_name = "contests"
    ordering = ["-event__date"]
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page_number = self.request.GET.get("page")
        context["page_obj"] = paginator.get_page(page_number)
        return context


class PredictionListView(ListView):
    model = Prediction
    template_name = "prediction_list.html"  # Replace with your template
    context_object_name = "predictions"
    ordering = ["-contest__event__date"]
    paginate_by = 20

    def get_queryset(self):
        return Prediction.objects.filter(user=self.request.user).order_by(
            "-contest__event__date"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page_number = self.request.GET.get("page")
        context["page_obj"] = paginator.get_page(page_number)
        return context


class PredictionDetailView(DetailView):
    model = Prediction
    template_name = "prediction_detail.html"  # Replace with your template
    context_object_name = "prediction"

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        return get_object_or_404(
            queryset, prediction_id=self.kwargs.get("prediction_id")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
