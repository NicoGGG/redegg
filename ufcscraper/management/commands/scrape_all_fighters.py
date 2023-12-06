from django.core.management.base import BaseCommand
from ufcscraper.tasks import scrape_ufc_fighters


class Command(BaseCommand):
    help = "Scrape all UFC fighters"

    def add_arguments(self, parser):
        parser.add_argument("fighters", nargs="*", type=str)

    def handle(self, *args, **kwargs):
        fighters = kwargs["fighters"]
        scrape_ufc_fighters.apply_async(args=[fighters])
        self.stdout.write(
            self.style.SUCCESS("Successfully triggered task to scrape all UFC fighters")
        )
