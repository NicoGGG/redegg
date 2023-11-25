import uuid
from django.test import TestCase
from redegg.models import Prognostic, Prediction, Contest
from ufcscraper.models import Fighter, Event, Fight
from django.contrib.auth.models import User
from django.db.models.signals import ModelSignal, pre_save, post_save

from ufcscraper.signals import (
    calculate_points_when_fight_over,
    update_contest_status,
    update_event_status,
)


class PrognosticModelTest(TestCase):
    def setUp(self):
        pre_save.disconnect(calculate_points_when_fight_over, sender=Fight)
        post_save.disconnect(update_event_status, sender=Fight)
        post_save.disconnect(update_contest_status, sender=Event)
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.fighter = Fighter.objects.create(
            first_name="Fighter",
            last_name="Name",
            win=1,
            loss=1,
            draw=1,
            fighter_id="1",
        )
        self.fighter1 = Fighter.objects.create(
            first_name="Fighter1",
            last_name="Name",
            win=1,
            loss=1,
            draw=1,
            fighter_id="2",
        )
        self.fighter2 = Fighter.objects.create(
            first_name="Fighter2",
            last_name="Name",
            win=1,
            loss=1,
            draw=1,
            fighter_id="3",
        )
        self.event = Event.objects.create(name="Event Name")
        self.fight = Fight.objects.create(
            event=self.event,
            fighter_one=self.fighter,
            fighter_two=self.fighter,
            position=1,
        )
        self.contest = Contest.objects.create(event=self.event, slug=str(uuid.uuid4()))
        self.prediction = Prediction.objects.create(
            user=self.user, contest=self.contest
        )
        self.prognostic = Prognostic.objects.create(
            prediction=self.prediction, fight=self.fight, fight_result=self.fighter
        )

    def tearDown(self):
        # Reconnect the signals
        pre_save.connect(calculate_points_when_fight_over, sender=Fight)
        post_save.connect(update_event_status, sender=Fight)
        post_save.connect(update_contest_status, sender=Event)

    def test_delete_fight_deletes_associated_prognostics(self):
        self.fight.delete()
        self.assertEqual(Prognostic.objects.filter(fight=self.fight).count(), 0)

    def test_calculate_points_main_event_won(self):
        self.fight.position = 1
        self.fight.winner = self.fighter1
        self.fight.save()
        self.prognostic.fight_result = self.fighter1
        self.prognostic.calculate_points()
        self.assertEqual(self.prognostic.points, 100)

    def test_calculate_points_main_event_loser(self):
        self.fight.position = 1
        self.fight.winner = self.fighter1
        self.fight.save()
        self.prognostic.fight_result = self.fighter2
        self.prognostic.calculate_points()
        self.assertEqual(self.prognostic.points, 0)

    def test_calculate_points_main_event_draw(self):
        self.fight.position = 1
        self.fight.winner = None
        self.fight.wl_fighter_one = "DRAW"
        self.fight.wl_fighter_two = "DRAW"
        self.fight.save()
        self.prognostic.fight_result = None
        self.prognostic.is_draw = True
        self.prognostic.calculate_points()
        self.assertEqual(self.prognostic.points, 100)

    def test_calculate_points_co_main_event_won(self):
        self.fight.position = 2
        self.fight.winner = self.fighter1
        self.fight.save()
        self.prognostic.fight_result = self.fighter1
        self.prognostic.calculate_points()
        self.assertEqual(self.prognostic.points, 50)

    def test_calculate_points_co_main_event_lost(self):
        self.fight.position = 2
        self.fight.winner = self.fighter1
        self.fight.save()
        self.prognostic.fight_result = self.fighter2
        self.prognostic.calculate_points()
        self.assertEqual(self.prognostic.points, 0)

    def test_calculate_points_co_main_event_draw(self):
        self.fight.position = 2
        self.fight.winner = None
        self.fight.wl_fighter_one = "DRAW"
        self.fight.wl_fighter_two = "DRAW"
        self.fight.save()
        self.prognostic.fight_result = None
        self.prognostic.is_draw = True
        self.prognostic.calculate_points()
        self.assertEqual(self.prognostic.points, 50)

    def test_calculate_points_main_card_won(self):
        self.fight.position = 3
        self.fight.winner = self.fighter1
        self.fight.save()
        self.prognostic.fight_result = self.fighter1
        self.prognostic.calculate_points()
        self.assertEqual(self.prognostic.points, 20)

    def test_calculate_points_main_card_lost(self):
        self.fight.position = 4
        self.fight.winner = self.fighter1
        self.fight.save()
        self.prognostic.fight_result = self.fighter2
        self.prognostic.calculate_points()
        self.assertEqual(self.prognostic.points, 0)

    def test_calculate_points_main_card_draw(self):
        self.fight.position = 5
        self.fight.winner = None
        self.fight.wl_fighter_one = "DRAW"
        self.fight.wl_fighter_two = "DRAW"
        self.fight.save()
        self.prognostic.fight_result = None
        self.prognostic.is_draw = True
        self.prognostic.calculate_points()
        self.assertEqual(self.prognostic.points, 20)

    def test_calculate_points_prelim_won(self):
        self.fight.position = 6
        self.fight.winner = self.fighter1
        self.fight.save()
        self.prognostic.fight_result = self.fighter1
        self.prognostic.calculate_points()
        self.assertEqual(self.prognostic.points, 10)

    def test_calculate_points_prelim_lost(self):
        self.fight.position = 7
        self.fight.winner = self.fighter1
        self.fight.save()
        self.prognostic.fight_result = self.fighter2
        self.prognostic.calculate_points()
        self.assertEqual(self.prognostic.points, -10)

    def test_calculate_points_prelim_draw(self):
        self.fight.position = 8
        self.fight.winner = None
        self.fight.wl_fighter_one = "DRAW"
        self.fight.wl_fighter_two = "DRAW"
        self.fight.save()
        self.prognostic.fight_result = None
        self.prognostic.is_draw = True
        self.prognostic.calculate_points()
        self.assertEqual(self.prognostic.points, 10)

    def test_calculate_bonus_percentage_method_won(self):
        self.fight.method = "KO/TKO"
        self.fight.save()
        self.prognostic.method = "ko_tko"
        self.prognostic.calculate_bonus_percentage()
        self.assertEqual(self.prognostic.bonus_percentage, 30)
        self.fight.method = "SUB"
        self.fight.save()
        self.prognostic.method = "submission"
        self.prognostic.calculate_bonus_percentage()
        self.assertEqual(self.prognostic.bonus_percentage, 30)

    def test_calculate_bonus_percentage_method_lost(self):
        self.fight.method = "KO/TKO"
        self.fight.save()
        self.prognostic.method = "submission"
        self.prognostic.calculate_bonus_percentage()
        self.assertEqual(self.prognostic.bonus_percentage, -30)

    def test_calculate_bonus_percentage_bonus_won(self):
        self.fight.bonus = "perf"
        self.fight.save()
        self.prognostic.bonus = "perf"
        self.prognostic.calculate_bonus_percentage()
        self.assertEqual(self.prognostic.bonus_percentage, 50)
        self.fight.bonus = "sub"
        self.fight.save()
        self.prognostic.bonus = "sub"
        self.prognostic.calculate_bonus_percentage()
        self.assertEqual(self.prognostic.bonus_percentage, 50)
        self.fight.bonus = "ko"
        self.fight.save()
        self.prognostic.bonus = "ko"
        self.prognostic.calculate_bonus_percentage()
        self.assertEqual(self.prognostic.bonus_percentage, 50)
        self.fight.bonus = "fight"
        self.fight.save()
        self.prognostic.bonus = "fight"
        self.prognostic.calculate_bonus_percentage()
        self.assertEqual(self.prognostic.bonus_percentage, 50)

    def test_calculate_bonus_percentage_bonus_lost(self):
        self.fight.bonus = "perf"
        self.fight.save()
        self.prognostic.bonus = "fight"
        self.prognostic.calculate_bonus_percentage()
        self.assertEqual(self.prognostic.bonus_percentage, -50)

    def test_calculate_bonus_percentage_bonus_none_won(self):
        self.prognostic.calculate_bonus_percentage()
        self.assertEqual(self.prognostic.bonus_percentage, 0)

    def test_calculate_bonus_percentage_bonus_none_lost(self):
        self.prognostic.bonus = "fight"
        self.prognostic.calculate_bonus_percentage()
        self.assertEqual(self.prognostic.bonus_percentage, -50)

    def test_calculate_bonus_percentage_bonus_none(self):
        self.prognostic.bonus = None
        self.fight.bonus = "perf"
        self.fight.save()
        self.prognostic.calculate_bonus_percentage()
        self.assertEqual(self.prognostic.bonus_percentage, 0)

    def test_calculate_bonus_percentage_method_lost_bonus_none(self):
        self.prognostic.method = "ko_tko"
        self.prognostic.bonus = None
        self.fight.method = "SUB"
        self.fight.bonus = "fight"
        self.fight.save()
        self.prognostic.calculate_points_and_bonus_percentage()
        self.assertEqual(self.prognostic.bonus_percentage, -30)


class PredictionTestCase(TestCase):
    def setUp(self):
        pre_save.disconnect(calculate_points_when_fight_over, sender=Fight)
        post_save.disconnect(update_event_status, sender=Fight)
        post_save.disconnect(update_contest_status, sender=Event)

        self.user = User.objects.create_user(username="testuser", password="12345")
        self.fighter = Fighter.objects.create(
            first_name="Fighter",
            last_name="Name",
            win=1,
            loss=1,
            draw=1,
            fighter_id="1",
        )
        self.fighter1 = Fighter.objects.create(
            first_name="Fighter1",
            last_name="Name",
            win=1,
            loss=1,
            draw=1,
            fighter_id="2",
        )
        self.fighter2 = Fighter.objects.create(
            first_name="Fighter2",
            last_name="Name",
            win=1,
            loss=1,
            draw=1,
            fighter_id="3",
        )
        self.event = Event.objects.create(name="Event Name")
        self.fight = Fight.objects.create(
            event=self.event,
            fighter_one=self.fighter,
            fighter_two=self.fighter,
            position=1,
        )
        self.contest = Contest.objects.create(event=self.event)
        self.prediction = Prediction.objects.create(
            user=self.user, contest=self.contest
        )
        self.prognostic1 = Prognostic.objects.create(
            prediction=self.prediction,
            fight=self.fight,
            fight_result=self.fighter,
            points=100,
            bonus_percentage=30,
        )
        self.prognostic2 = Prognostic.objects.create(
            prediction=self.prediction,
            fight=self.fight,
            fight_result=self.fighter,
            points=50,
            bonus_percentage=50,
        )
        self.prognostic3 = Prognostic.objects.create(
            prediction=self.prediction,
            fight=self.fight,
            fight_result=self.fighter,
            points=-10,
            bonus_percentage=0,
        )

    def tearDown(self):
        # Delete the objects
        pre_save.connect(calculate_points_when_fight_over, sender=Fight)
        post_save.connect(update_event_status, sender=Fight)
        post_save.connect(update_contest_status, sender=Event)

    def test_calculate_points(self):
        self.prediction.calculate_points()
        self.assertEqual(self.prediction.points, 140)

    def test_calculate_bonus_modifier(self):
        self.prediction.calculate_bonus_modifier()
        self.assertEqual(self.prediction.bonus_modifier, 80)

    def test_calculate_bonus_modifier_zero(self):
        self.prognostic2.bonus_percentage = -50
        self.prognostic2.save()
        self.prediction.calculate_bonus_modifier()
        self.assertEqual(self.prediction.bonus_modifier, 0)

    def test_calculate_score(self):
        self.prediction.calculate_score()
        self.assertEqual(self.prediction.score, 252)
