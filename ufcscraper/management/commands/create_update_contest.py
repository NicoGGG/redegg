from django.core.management.base import BaseCommand
from ufcscraper.utils import create_or_update_contest


class Command(BaseCommand):
    help = "Create or update a contest for a given event"

    def add_arguments(self, parser):
        parser.add_argument("event_id", type=str, help="The UFC event ID")

    def handle(self, *args, **kwargs):
        event_id = kwargs["event_id"]
        create_or_update_contest(event_id)
