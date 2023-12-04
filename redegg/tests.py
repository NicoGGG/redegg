import uuid
from django.test import TestCase
from redegg.models import Prognostic, Prediction, Contest
from ufcscraper.models import Fighter, Event, Fight
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save, post_delete

from ufcscraper.signals import (
    calculate_points_when_fight_over,
    post_delete_handler,
    update_contest_status,
    update_event_status,
    update_fighters_in_created_fight,
    update_fighters_when_event_completed,
)


class PrognosticModelTest(TestCase):
    def setUp(self):
        pre_save.disconnect(calculate_points_when_fight_over, sender=Fight)
        pre_save.disconnect(update_fighters_when_event_completed, sender=Event)
        post_save.disconnect(update_event_status, sender=Fight)
        post_save.disconnect(update_contest_status, sender=Event)
        post_save.disconnect(update_fighters_in_created_fight, sender=Fight)
        post_delete.disconnect(post_delete_handler, sender=Fight)

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
        pre_save.connect(update_fighters_when_event_completed, sender=Event)
        post_save.connect(update_event_status, sender=Fight)
        post_save.connect(update_contest_status, sender=Event)
        post_save.connect(update_fighters_in_created_fight, sender=Fight)
        post_delete.connect(post_delete_handler, sender=Fight)

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
        pre_save.disconnect(update_fighters_when_event_completed, sender=Event)
        post_save.disconnect(update_event_status, sender=Fight)
        post_save.disconnect(update_contest_status, sender=Event)
        post_save.disconnect(update_fighters_in_created_fight, sender=Fight)
        post_delete.disconnect(post_delete_handler, sender=Fight)

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
        self.fight1 = Fight.objects.create(
            event=self.event,
            fight_id="1",
            fighter_one=self.fighter,
            fighter_two=self.fighter,
            position=1,
        )
        self.fight2 = Fight.objects.create(
            event=self.event,
            fight_id="2",
            fighter_one=self.fighter1,
            fighter_two=self.fighter2,
            position=2,
        )
        self.contest = Contest.objects.create(event=self.event)
        self.prediction = Prediction.objects.create(
            user=self.user, contest=self.contest
        )
        self.prognostic1 = Prognostic.objects.create(
            prediction=self.prediction,
            fight=self.fight1,
            fight_result=self.fighter,
            points=100,
            bonus_percentage=30,
            fight_result_won=True,
        )
        self.prognostic2 = Prognostic.objects.create(
            prediction=self.prediction,
            fight=self.fight1,
            fight_result=self.fighter,
            points=50,
            bonus_percentage=50,
            fight_result_won=True,
        )
        self.prognostic3 = Prognostic.objects.create(
            prediction=self.prediction,
            fight=self.fight1,
            fight_result=self.fighter,
            points=-10,
            bonus_percentage=0,
            fight_result_won=False,
        )
        self.prognostic4 = Prognostic.objects.create(
            prediction=self.prediction,
            fight=self.fight2,
            fight_result=self.fighter2,
            points=50,
            bonus_percentage=0,
            fight_result_won=True,
        )

    def tearDown(self):
        # Reconnect the signals
        pre_save.connect(calculate_points_when_fight_over, sender=Fight)
        pre_save.connect(update_fighters_when_event_completed, sender=Event)
        post_save.connect(update_event_status, sender=Fight)
        post_save.connect(update_contest_status, sender=Event)
        post_save.connect(update_fighters_in_created_fight, sender=Fight)
        post_delete.connect(post_delete_handler, sender=Fight)

    def test_calculate_points(self):
        self.prediction.calculate_points()
        self.assertEqual(self.prediction.points, 190)

    def test_calculate_bonus_modifier(self):
        self.prediction.calculate_bonus_modifier()
        self.assertEqual(self.prediction.bonus_modifier, 100)

    def test_calculate_bonus_modifier_zero(self):
        self.prognostic1.bonus_percentage = -30
        self.prognostic1.save()
        self.prognostic2.bonus_percentage = -50
        self.prognostic2.save()
        self.prediction.calculate_bonus_modifier()
        self.assertEqual(self.prediction.bonus_modifier, 0)

    def test_calculate_score(self):
        self.prediction.calculate_score()
        self.assertEqual(self.prediction.score, 380)

    def test_calculate_score_negative(self):
        self.prognostic1.points = 0
        self.prognostic2.points = 0
        self.prognostic3.points = 0
        self.prognostic4.points = -10
        self.prognostic1.save()
        self.prognostic2.save()
        self.prognostic3.save()
        self.prognostic4.save()
        self.prediction.calculate_score()
        self.assertEqual(self.prediction.score, 0)
