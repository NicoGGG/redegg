from django.core.management.base import BaseCommand
from ufcscraper.models import Event
from redegg.models import Contest


class Command(BaseCommand):
    help = "Create or update a contest for a given event"

    def add_arguments(self, parser):
        parser.add_argument("event_id", type=str, help="The UFC event ID")

    def handle(self, *args, **kwargs):
        event_id = kwargs["event_id"]
        self.stdout.write(
            self.style.NOTICE(f"Create/Update contest for event {event_id}")
        )

        try:
            # Fetch the event.
            event = Event.objects.get(event_id=event_id)
            if event.completed:
                status = "closed"
            elif event.upcoming:
                status = "open"
            else:
                status = "live"
            # Create or update the contest.
            contest, created = Contest.objects.update_or_create(
                event=event,
                defaults={
                    "status": status,
                },
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully created contest {contest.id} for event {event_id}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully updated contest {contest.id} for event {event_id}"
                    )
                )
        except Event.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"Event {event_id} does not exist in the database")
            )
