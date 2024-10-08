from django.core.management.base import BaseCommand
from ufcscraper.tasks import scrape_ufc_events


class Command(BaseCommand):
    help = "Scrape last n UFC event"

    def add_arguments(self, parser):
        parser.add_argument(
            "--last", type=int, help="Last n event scrape", default=1, required=False
        )

    def handle(self, *args, **kwargs):
        last = kwargs["last"]
        scrape_ufc_events.apply_async(args=[last])
        self.stdout.write(
            self.style.SUCCESS(
                "Successfully triggered task to scrape upcoming UFC event"
            )
        )
