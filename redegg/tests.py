from django.test import TestCase
from redegg.models import Prognostic, Prediction, Contest
from ufcscraper.models import Fighter, Event, Fight
from django.contrib.auth.models import User


class PrognosticModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.fighter = Fighter.objects.create(
            first_name="Fighter", last_name="Name", win=1, loss=1, draw=1
        )
        self.event = Event.objects.create(name="Event Name")
        self.fight = Fight.objects.create(
            event=self.event, fighter_one=self.fighter, fighter_two=self.fighter
        )
        self.contest = Contest.objects.create(event=self.event)
        self.prediction = Prediction.objects.create(
            user=self.user, contest=self.contest
        )
        self.prognostic = Prognostic.objects.create(
            prediction=self.prediction, fight=self.fight, fight_result=self.fighter
        )

    def test_delete_fight_deletes_associated_prognostics(self):
        self.fight.delete()
        self.assertEqual(Prognostic.objects.filter(fight=self.fight).count(), 0)
