from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from ufcscraper.models import Event, Fight
from ufcscraper.tasks import scrape_ufc_fighters
from ufcscraper.utils import create_or_update_contest, send_discord_notification


@receiver(pre_save, sender=Event)
@send_discord_notification
def update_fighters_when_event_completed(sender, instance, **kwargs):
    try:
        # Get the old instance from the database
        old_instance = Event.objects.get(pk=instance.pk)
    except Event.DoesNotExist:
        # The instance is not in the database (probably it's being created)
        return
    if not old_instance.completed and instance.completed:
        related_fights = Fight.objects.filter(event=instance)
        fighters = [
            fighter_id
            for fight in related_fights
            for fighter_id in (
                fight.fighter_one.fighter_id,
                fight.fighter_two.fighter_id,
            )
        ]
        scrape_ufc_fighters.apply_async(args=[fighters])
        message = f"Updating fighters participating in event {instance} - {instance.id}"
        print(message)
        return message


@receiver(post_save, sender=Event)
@send_discord_notification
def update_contest_status(sender, instance, **kwargs):
    """
    If an event is not upcoming and not completed, contest status should be changed to 'live'
    If an event is completed, contest status should be changed to 'closed'
    """
    return create_or_update_contest(str(instance.event_id))


@receiver(post_save, sender=Fight)
@send_discord_notification
def update_event_status(sender, instance, **kwargs):
    related_fights = Fight.objects.filter(event=instance.event)
    upcoming = instance.event.upcoming
    completed = instance.event.completed
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
    if upcoming != instance.event.upcoming or completed != instance.event.completed:
        message = f"Event status updated to upcoming={instance.event.upcoming} and completed={instance.event.completed}"
        return message


@receiver(pre_save, sender=Fight)
def calculate_points_when_fight_over(sender, instance, **kwargs):
    try:
        # Get the old instance from the database
        old_instance = Fight.objects.get(pk=instance.pk)
    except Fight.DoesNotExist:
        # The instance is not in the database (probably it's being created)
        return
    if not old_instance.is_over() and instance.is_over():
        print(f"Calculating points for fight {instance.fight_id}")
        prognostics = instance.prognostic_set.all()
        for prognostic in prognostics:
            prognostic.calculate_points_and_bonus_percentage()
            prognostic.save()
            prognostic.prediction.calculate_score()
            prognostic.prediction.save()


@receiver(post_save, sender=Fight)
@send_discord_notification
def update_fighters_in_created_fight(sender, instance, created, **kwargs):
    if created:
        fighters = [instance.fighter_one.fighter_id, instance.fighter_two.fighter_id]
        scrape_ufc_fighters.apply_async(args=[fighters])
        message = f"Updating fighters {fighters} participating in fight {instance} - {instance.id}"
        print(message)
        return message


@receiver(post_delete, sender=Fight)
@send_discord_notification
def post_delete_handler(sender, instance, **kwargs):
    message = f"A Fight instance was deleted: Event={instance.event}, Name={instance}"
    print(message)
    return message
