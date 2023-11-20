# ufcscraper/management/commands/scrape_event_fights.py
from django.core.management.base import BaseCommand
from ufcscraper.tasks import scrape_ufc_event_fights


class Command(BaseCommand):
    help = "Scrape UFC event fights"

    def add_arguments(self, parser):
        parser.add_argument(
            "event_id", type=str, help="The ID of the event to scrape fights for"
        )

    def handle(self, *args, **kwargs):
        event_id = kwargs["event_id"]
        scrape_ufc_event_fights.apply_async(args=[event_id])
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully triggered task to scrape fights for event {event_id}"
            )
        )
