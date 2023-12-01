from functools import wraps
from ufcapi.settings import DISCORD_WEBHOOK_URL
from ufcscraper.models import Event
from redegg.models import Contest
from ufcscraper.tasks import send_notification_to_webhook


def send_discord_notification(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        message = func(*args, **kwargs)
        url = DISCORD_WEBHOOK_URL
        if message and url:
            send_notification_to_webhook.delay(url, message)

        return message

    return wrapper


def create_or_update_contest(event_id: str):
    message = ""
    try:
        # Fetch the event.
        event = Event.objects.get(event_id=event_id)
        if event.completed:
            status = "closed"
        elif event.upcoming:
            status = "open"
        else:
            status = "live"
        # Fetch old contest if it exists.
        try:
            old_contest = event.contest
        except Event.contest.RelatedObjectDoesNotExist:
            # No contest exists for this event. It is being created.
            pass
        # Create or update the contest.
        contest, created = Contest.objects.update_or_create(
            event=event,
            defaults={
                "status": status,
            },
        )

        if created:
            message = f"Successfully created contest {contest} for event {event_id}"
        elif old_contest.status != contest.status:
            message = f"Successfully updated contest {contest} for event {event_id} to status: {contest.status}"
    except Event.DoesNotExist:
        message = f"Event {event_id} does not exist in the database"
    if message:
        print(message)
    return message
