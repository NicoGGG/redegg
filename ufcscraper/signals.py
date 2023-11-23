from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from ufcscraper.models import Event, Fight


@receiver(post_save, sender=Fight)
def update_event_status(sender, instance, **kwargs):
    related_fights = Fight.objects.filter(event=instance.event)

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


# @receiver(post_save, sender=Event)
# def update_contest_status(sender, instance, **kwargs):
#     """
#     If an event is not upcoming and not completed, contest status should be changed to 'live'
#     If an event is completed, contest status should be changed to 'finished'
#     """
#     if not instance.upcoming and not instance.completed:
#         instance.contest_status = "live"
#     elif instance.completed:
#         instance.contest_status = "finished"
#     instance.save()


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
