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
            contest = Contest.objects.get(id=contest_id)
            contest.calculate_all_predictions_scores()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
        else:
            self.stdout.write(self.style.SUCCESS("Success"))
