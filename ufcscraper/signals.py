from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.management import call_command
from ufcscraper.models import Event, Fight
from redegg.models import Contest


@receiver(post_save, sender=Fight)
def update_event_status(sender, instance, **kwargs):
    related_fights = Fight.objects.filter(event=instance.event)
    print("Updating event status")
    if any(
        fight.wl_fighter_one is not None and fight.wl_fighter_two is not None
        for fight in related_fights
    ):
        instance.event.upcoming = False
    else:
        instance.event.upcoming = True
    if all(
        fight.wl_fighter_one is not None and fight.wl_fighter_two is not None
        for fight in related_fights
    ):
        instance.event.completed = True
    else:
        instance.event.completed = False
    instance.event.save()


@receiver(post_save, sender=Event)
def update_contest_status(sender, instance, **kwargs):
    """
    If an event is not upcoming and not completed, contest status should be changed to 'live'
    If an event is completed, contest status should be changed to 'finished'
    """
    contest = Contest.objects.filter(event=instance).first()
    if contest:
        print("Updating contest status")
        if instance.upcoming:
            contest.status = "open"
            contest.save()
        if not instance.upcoming and not instance.completed:
            contest.status = "live"
            contest.save()
        elif instance.completed:
            contest.status = "closed"
            contest.save()
    else:
        # Create contest for the event
        call_command("create_update_contest", str(instance.event_id))


## Signal that executes when an Event is created, sending the info to a Google Cloud Function
# @receiver(post_save, sender=Event)
# def event_post_save(sender, instance: Event, created, **kwargs):
#     if created:
#         print("Event created, sending to Google Cloud Function")
#         # requests.post(
#         #     "https://us-central1-ufc-api-293821.cloudfunctions.net/ufcapi",
#         #     data=instance,
#         # )
#     else:
#         print("Event updated, sending to Google Cloud Function")
#         # requests.post(
#         #     "https://us-central1-ufc-api-293821.cloudfunctions.net/ufcapi",
#         #     data=instance,
#         # )
