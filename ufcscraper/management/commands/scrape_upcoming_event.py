# ufcscraper/management/commands/scrape_upcoming_event.py
from django.core.management.base import BaseCommand
from ufcscraper.tasks import scrape_upcoming_ufc_event


class Command(BaseCommand):
    help = "Scrape upcoming UFC event"

    def handle(self, *args, **kwargs):
        scrape_upcoming_ufc_event.apply_async()
        self.stdout.write(
            self.style.SUCCESS(
                "Successfully triggered task to scrape upcoming UFC event"
            )
        )
