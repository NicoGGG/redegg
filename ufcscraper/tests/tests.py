from django.test import TestCase
import requests
from ufcscraper.models import Event, Fight, Fighter
from ufcscraper.scrapers import get_fighter_photo_url, scrap_fights_from_event
from ufcscraper.tests.test_utils import assert_fight

from django.db.models.signals import pre_save, post_save, post_delete

from ufcscraper.signals import (
    calculate_points_when_fight_over,
    post_delete_handler,
    update_contest_status,
    update_event_status,
    update_fighters_in_created_fight,
    update_fighters_when_event_completed,
)


class ScraperTest(TestCase):
    def setUp(self):
        # Disconnect all signals
        pre_save.disconnect(calculate_points_when_fight_over, sender=Fight)
        pre_save.disconnect(update_fighters_when_event_completed, sender=Event)
        post_save.disconnect(update_event_status, sender=Fight)
        post_save.disconnect(update_contest_status, sender=Event)
        post_save.disconnect(update_fighters_in_created_fight, sender=Fight)
        post_delete.disconnect(post_delete_handler, sender=Fight)

        with open("ufcscraper/tests/fixtures/event_2ce6541127b0e232_test.html") as file:
            self.test_2ce6541127b0e232_html = file.read()
        with open("ufcscraper/tests/fixtures/event_8fa2b06572365321_test.html") as file:
            self.test_8fa2b06572365321_html = file.read()
        Fighter.objects.create(
            link="http://ufcstats.com/fighter-details/07f72a2a7591b409",
            fighter_id="07f72a2a7591b409",
            first_name="Jon",
            last_name="Jones",
            nickname="Bones",
            height="6' 4\"",
            weight="248 lbs.",
            reach='84.0"',
            stance="Orthodox",
            belt=True,
            win=27,
            loss=1,
            draw=0,
        )
        Fighter.objects.create(
            link="http://ufcstats.com/fighter-details/93fe7332d16c6ad9",
            fighter_id="93fe7332d16c6ad9",
            first_name="Tom",
            last_name="Aaron",
            nickname="",
            height="--",
            weight="155 lbs.",
            reach="--",
            stance="",
            belt=False,
            win=5,
            loss=3,
            draw=0,
        )
        self.jj = Fighter.objects.get(fighter_id="07f72a2a7591b409")
        self.ta = Fighter.objects.get(fighter_id="93fe7332d16c6ad9")
        self.test_fighter_page_jj = requests.get(
            "https://liveapi.yext.com/v2/accounts/me/answers/vertical/query?experienceKey=answers-en&api_key=850a88aeb3c29599ce2db46832aa229f&v=20220511&version=PRODUCTION&locale=en&input=Jon+Jones&verticalKey=athletes&limit=21&offset=0&retrieveFacets=true&facetFilters=%7B%7D&session_id=3ed6799e-6cad-46ea-9137-d9bd11417549&sessionTrackingEnabled=true&sortBys=%5B%5D&referrerPageUrl=https%3A%2F%2Fwww.ufc.com%2F&source=STANDARD&jsLibVersion=v1.14.3"
        )
        self.test_fighter_page_ta = requests.get(
            "https://liveapi.yext.com/v2/accounts/me/answers/vertical/query?experienceKey=answers-en&api_key=850a88aeb3c29599ce2db46832aa229f&v=20220511&version=PRODUCTION&locale=en&input=Tom+Aaron&verticalKey=athletes&limit=21&offset=0&retrieveFacets=true&facetFilters=%7B%7D&session_id=3ed6799e-6cad-46ea-9137-d9bd11417549&sessionTrackingEnabled=true&sortBys=%5B%5D&referrerPageUrl=https%3A%2F%2Fwww.ufc.com%2F&source=STANDARD&jsLibVersion=v1.14.3"
        )

    def tearDown(self):
        # Reconnect the signals
        pre_save.connect(calculate_points_when_fight_over, sender=Fight)
        pre_save.connect(update_fighters_when_event_completed, sender=Event)
        post_save.connect(update_event_status, sender=Fight)
        post_save.connect(update_contest_status, sender=Event)
        post_save.connect(update_fighters_in_created_fight, sender=Fight)
        post_delete.connect(post_delete_handler, sender=Fight)

    def test_scrap_fights_from_event_2ce6541127b0e232(self):
        fights = scrap_fights_from_event(
            self.test_2ce6541127b0e232_html, "2ce6541127b0e232"
        )
        expected_fight_1 = {
            "event": "2ce6541127b0e232",
            "fight_id": "05e2832cd5ffb7a6",
            "link": "http://ufcstats.com/fight-details/05e2832cd5ffb7a6",
            "fighter_one_id": "150ff4cc642270b9",
            "fighter_two_id": "07225ba28ae309b6",
            "weight_class": "Featherweight",
            "method": "KO/TKO",
            "round": 1,
            "time": "1:39",
            "belt": False,
            "bonus": None,
            "wl_fighter_one": "W",
            "wl_fighter_two": "L",
        }
        expected_fight_2 = {
            "event": "2ce6541127b0e232",
            "fight_id": "2c01f4df404ff6ee",
            "link": "http://ufcstats.com/fight-details/2c01f4df404ff6ee",
            "fighter_one_id": "84b3e7d38f2d2ec5",
            "fighter_two_id": "5866fc86183a9fb8",
            "weight_class": "Welterweight",
            "method": "U-DEC",
            "round": 3,
            "time": "5:00",
            "belt": False,
            "bonus": None,
            "wl_fighter_one": "W",
            "wl_fighter_two": "L",
        }
        expected_fight_3 = {
            "event": "2ce6541127b0e232",
            "fight_id": "499557c33e67deaf",
            "link": "http://ufcstats.com/fight-details/499557c33e67deaf",
            "fighter_one_id": "9fa3bd637edd9aa2",
            "fighter_two_id": "6da99156486ed6c2",
            "weight_class": "Welterweight",
            "method": "KO/TKO",
            "round": 3,
            "time": "1:26",
            "belt": False,
            "bonus": "fight",
            "wl_fighter_one": "W",
            "wl_fighter_two": "L",
        }
        assert_fight(self, fights[0], expected_fight_1)
        assert_fight(self, fights[1], expected_fight_2)
        assert_fight(self, fights[2], expected_fight_3)

    def test_scrap_fights_from_event_8fa2b06572365321(self):
        fights = scrap_fights_from_event(
            self.test_8fa2b06572365321_html, "8fa2b06572365321"
        )
        # Fight 1 Shevshenko vs Grasso, Title fight ends in a draw
        expected_fight_1 = {
            "event": "8fa2b06572365321",
            "fight_id": "b395c89e19a3fec4",
            "link": "http://ufcstats.com/fight-details/b395c89e19a3fec4",
            "fighter_one_id": "e8b731feff72294b",
            "fighter_two_id": "132deb59abae64b1",
            "weight_class": "Women's Flyweight",
            "method": "S-DEC",
            "round": 5,
            "time": "5:00",
            "belt": True,
            "bonus": None,
            "wl_fighter_one": "DRAW",
            "wl_fighter_two": "DRAW",
        }
        # Fight 4 Daniel Zellhuber vs Christos Giagos, Zellhuber wins by SUB, Perf of the night
        expected_fight_4 = {
            "event": "8fa2b06572365321",
            "fight_id": "2e1435c160bfe8b2",
            "link": "http://ufcstats.com/fight-details/2e1435c160bfe8b2",
            "fighter_one_id": "4148802ae4a50768",
            "fighter_two_id": "de45aaae23dfa392",
            "weight_class": "Lightweight",
            "method": "SUB",
            "round": 2,
            "time": "3:26",
            "belt": False,
            "bonus": "perf",
            "wl_fighter_one": "W",
            "wl_fighter_two": "L",
        }
        # Fight 8 Edgar Chairez vs Daniel Lacerda, NC overturned later
        expected_fight_8 = {
            "event": "8fa2b06572365321",
            "fight_id": "5d3e046b6bcd49f5",
            "link": "http://ufcstats.com/fight-details/5d3e046b6bcd49f5",
            "fighter_one_id": "5ef94841c4bc3f86",
            "fighter_two_id": "31bb0772f21cabd8",
            "weight_class": "Flyweight",
            "method": "Overturned",
            "round": 1,
            "time": "3:47",
            "belt": False,
            "bonus": None,
            "wl_fighter_one": "NC",
            "wl_fighter_two": "NC",
        }
        assert_fight(self, fights[0], expected_fight_1)
        assert_fight(self, fights[3], expected_fight_4)
        assert_fight(self, fights[7], expected_fight_8)

    def test_get_fighter_photo(self):
        fighter_photo_jj = get_fighter_photo_url(self.test_fighter_page_jj)
        self.assertEqual(
            fighter_photo_jj,
            "https://a.mktgcdn.com/p/npb85iT_87YpkyNWSEiU63gGv9ZHY2ONFqsRIxrWyEk/520x325.png",
        )

    def test_get_fighter_photo_no_photo(self):
        fighter_photo_ta = get_fighter_photo_url(self.test_fighter_page_ta)
        self.assertEqual(
            fighter_photo_ta,
            "https://www.ufc.com/themes/custom/ufc/assets/img/no-profile-image.png",
        )
