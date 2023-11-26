from django.db.models.signals import post_save, pre_save
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
    call_command("create_update_contest", str(instance.event_id))


@receiver(pre_save, sender=Fight)
def calculate_points_when_fight_over(sender, instance, **kwargs):
    if instance.pk and instance.is_over():
        print(f"Calculating points for fight {instance.fight_id}")
        prognostics = instance.prognostic_set.all()
        for prognostic in prognostics:
            prognostic.calculate_points_and_bonus_percentage()
            prognostic.save()
            prognostic.prediction.calculate_score()
            prognostic.prediction.save()
