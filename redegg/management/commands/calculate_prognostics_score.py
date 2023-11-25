from django.core.management.base import BaseCommand

from redegg.models import Contest


class Command(BaseCommand):
    help = "Calculate the prognostics score for a contest"

    def add_arguments(self, parser):
        parser.add_argument("contest_id", type=int, help="The Django contest ID")

    def handle(self, *args, **kwargs):
        contest_id = kwargs["contest_id"]
        self.stdout.write(
            self.style.NOTICE(f"Calculating prognostics score for contest {contest_id}")
        )
        try:
            # Fetch the contest.
            contest = Contest.objects.get(id=contest_id)

            # Fetch the predictions and prognostics of all users for the contest.
            predictions = contest.prediction_set.all()

            for prediction in predictions:
                prognostics = prediction.prognostic_set.all()
                # Calculate the score for each prognostic.
                for prognostic in prognostics:
                    if prognostic:
                        prognostic.calculate_points()
                        prognostic.calculate_bonus_percentage()
                        prognostic.save()
                # Calculate the score for the prediction.
                prediction.calculate_score()
                prediction.save()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
        else:
            self.stdout.write(self.style.SUCCESS("Success"))
