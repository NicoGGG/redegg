import time
from celery import shared_task
from django.db import OperationalError
from ufcscraper.models import Event, Fighter, Fight, Country
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from ufcscraper.scrapers import (
    get_fighter_photo_url,
    scrap_fights_from_event,
    get_fighter_country,
)


@shared_task(
    autoretry_for=(OperationalError, requests.RequestException),
    rate_limit="3/s",
    retry_kwargs={"max_retries": 5},
)
def send_notification_to_webhook(url: str, message: str):
    requests.post(url, json={"content": message})
    print(f"Notification sent: {message}")


@shared_task(
    serializer="json",
    retry_kwargs={"max_retries": 1},
)
def save_all_fights_from_event(fights, event_id: str):
    event = Event.objects.get(event_id=event_id)

    # Fetch all existing fights for the event.
    existing_fights = Fight.objects.filter(event=event)

    # Convert the new fights to a set for easier comparison.
    new_fights = set(fight["fight_id"] for fight in fights)

    # Delete any existing fights that are not in the new fights.
    for fight in existing_fights:
        if fight.fight_id not in new_fights:
            fight.delete()

    for index, fight in enumerate(fights):
        fight_data = {
            **fight,
            "event": event,
            "position": index + 1,
            "winner": None,
        }
        old_fight = Fight.objects.filter(fight_id=fight["fight_id"]).first()
        if old_fight:
            # Preserve the order of fighters in the fight.
            fighter_one = Fighter.objects.get(id=old_fight.fighter_one.id)
            fighter_two = Fighter.objects.get(id=old_fight.fighter_two.id)
            fight_data["fighter_one"] = fighter_one
            fight_data["fighter_two"] = fighter_two
            if old_fight.fighter_one.fighter_id == fight["fighter_one_id"]:
                fight_data["wl_fighter_one"] = fight["wl_fighter_one"]
                fight_data["wl_fighter_two"] = fight["wl_fighter_two"]
            else:
                fight_data["wl_fighter_one"] = fight["wl_fighter_two"]
                fight_data["wl_fighter_two"] = fight["wl_fighter_one"]
        else:
            try:
                fighter_one = Fighter.objects.get(fighter_id=fight["fighter_one_id"])
                fighter_two = Fighter.objects.get(fighter_id=fight["fighter_two_id"])
            except Fighter.DoesNotExist:
                # If a fighter does not exist, scrape it.
                print(f"Fighters missing for fight {fight['fight_id']} - scraping...")
                scrape_ufc_fighters([fight["fighter_one_id"], fight["fighter_two_id"]])
                fighter_one = Fighter.objects.get(fighter_id=fight["fighter_one_id"])
                fighter_two = Fighter.objects.get(fighter_id=fight["fighter_two_id"])
            fight_data["fighter_one"] = fighter_one

            fight_data["fighter_two"] = fighter_two

        if fight_data["wl_fighter_one"] == "W":
            fight_data["winner"] = fighter_one
        elif fight_data["wl_fighter_two"] == "W":
            fight_data["winner"] = fighter_two

        fight_data.pop("fighter_one_id")
        fight_data.pop("fighter_two_id")
        fight_data.pop("fight_id")
        Fight.objects.update_or_create(
            fight_id=fight["fight_id"],
            defaults=fight_data,
        )

        print(f"Fight {fight['fight_id']} saved")

    return print(f"Fights from event {event_id} saved")


# scraping function for fights in an event
@shared_task(
    bind=True,
    autoretry_for=(OperationalError, requests.RequestException),
    rate_limit="3/s",
    retry_kwargs={"max_retries": 5},
)
def scrape_ufc_event_fights(self, event_id: str):
    print(f"Scraping fights from event {event_id}")
    url = f"http://ufcstats.com/event-details/{event_id}"
    try:
        page = requests.get(url)
        if page.status_code != 200:
            print(
                f"Error scraping fights from event {event_id}. Error code: {page.status_code}"
            )
            raise requests.RequestException(
                f"Error scraping fights from event {event_id}. Status code: {page.status_code}"
            )
        fight_list = scrap_fights_from_event(page.content, event_id)
        return save_all_fights_from_event(fight_list, event_id)
    except Exception as exc:
        print(f"Error scraping fights from event {event_id}. Error: {exc}")
        raise self.retry(exc=exc)


# saving function for events
@shared_task(serializer="json")
def save_events(events):
    for event in events:
        Event.objects.update_or_create(
            event_id=event["event_id"],
            defaults={
                "name": event["name"],
                "link": event["link"],
                "date": event["date"],
                "type": event["type"],
                "location": event["location"],
            },
        )
        scrape_ufc_event_fights.delay(event["event_id"])  # type: ignore
    return print("Events saved")


# saving function for fighters
@shared_task(serializer="json")
def save_fighters(fighters):
    for fighter in fighters:
        Fighter.objects.update_or_create(
            fighter_id=fighter["fighter_id"],
            defaults={
                "first_name": fighter["first_name"],
                "last_name": fighter["last_name"],
                "nickname": fighter["nickname"],
                "link": fighter["link"],
                "height": fighter["height"],
                "weight": fighter["weight"],
                "reach": fighter["reach"],
                "stance": fighter["stance"],
                "belt": fighter["belt"],
                "win": fighter["win"],
                "loss": fighter["loss"],
                "draw": fighter["draw"],
                "photo_url": fighter["photo_url"],
                "country": fighter.get("country", None),
            },
        )
    return print("Fighters saved")


# scraping function for fighters
@shared_task(
    autoretry_for=(OperationalError, AttributeError),
    rate_limit="1/s",
    retry_kwargs={"max_retries": 5},
    default_retry_delay=30,
)
def scrape_ufc_fighters(fighters: list[str] = []):
    """
    Takes a list of fighter ids to scrape. If the list is empty, it scrapes all fighters.
    """
    fighter_list = []
    chars = "abcdefghijklmnopqrstuvwxyz"
    for char in chars:
        url = f"http://ufcstats.com/statistics/fighters?char={char}&page=all"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        table = soup.find("table", class_="b-statistics__table")
        rows_body = table.find("tbody")  # type: ignore
        rows = rows_body.find_all("tr")  # type: ignore
        # pop the first row because it is an empty line for some reason
        rows.pop(0)
        for row in rows:
            cells = row.find_all("td")
            if len(cells) > 0:
                first_name = cells[0].text.strip()
                last_name = cells[1].text.strip()
                nickname = cells[2].text.strip()
                link = cells[0].find("a")["href"]
                fighter_id = link.split("/")[-1]
                height = cells[3].text.strip()
                weight = cells[4].text.strip()
                reach = cells[5].text.strip()
                stance = cells[6].text.strip()
                win = cells[7].text.strip()
                loss = cells[8].text.strip()
                draw = cells[9].text.strip()
                belt = cells[10].find("img", class_="b-list__icon") is not None
                fighter = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "nickname": nickname,
                    "link": link,
                    "fighter_id": fighter_id,
                    "height": height,
                    "weight": weight,
                    "reach": reach,
                    "stance": stance,
                    "win": win,
                    "loss": loss,
                    "draw": draw,
                    "belt": belt,
                }
                if len(fighters) > 0 and fighter["fighter_id"] not in fighters:
                    continue

                # get fighter photo
                time.sleep(0.1)
                live_api_response = requests.get(
                    f"https://liveapi.yext.com/v2/accounts/me/answers/vertical/query?experienceKey=answers-en&api_key=850a88aeb3c29599ce2db46832aa229f&v=20220511&version=PRODUCTION&locale=en&input={first_name}+{last_name}&verticalKey=athletes&limit=21&offset=0&retrieveFacets=true&facetFilters=%7B%7D&session_id=3ed6799e-6cad-46ea-9137-d9bd11417549&sessionTrackingEnabled=true&sortBys=%5B%5D&referrerPageUrl=https%3A%2F%2Fwww.ufc.com%2F&source=STANDARD&jsLibVersion=v1.14.3"
                )
                photo_url = get_fighter_photo_url(live_api_response)
                fighter["photo_url"] = photo_url
                country_dict = get_fighter_country(live_api_response)
                if country_dict:
                    country, created = Country.objects.get_or_create(**country_dict)
                    fighter["country"] = country
                print(
                    f"Fighter {fighter['fighter_id']} - {fighter['first_name']} {fighter['last_name']} - scraped"
                )
                fighter_list.append(fighter)
    return save_fighters(fighter_list)


# scraping function for events
@shared_task(
    autoretry_for=(OperationalError, AttributeError),
    rate_limit="3/s",
    retry_kwargs={"max_retries": 5},
)
def scrape_ufc_events(last: int = 10):
    event_list = []
    url = "http://ufcstats.com/statistics/events/completed?page=all"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    table = soup.find("table", class_="b-statistics__table-events")

    rows_body = table.find("tbody")  # type: ignore
    rows = rows_body.find_all("tr")  # type: ignore
    # pop the first row because it is an empty line for some reason
    rows.pop(0)
    i = 0
    for row in rows:
        cells = row.find_all("td")
        if len(cells) > 0:
            name = cells[0].find("a").text.strip()
            link = cells[0].find("a")["href"]
            event_id = link.split("/")[-1]
            date = cells[0].find("span", class_="b-statistics__date").text.strip()
            type = "Fight Night" if "Fight Night" in name else "UFC"
            location = cells[1].text.strip()
            event = {
                "name": name,
                "link": link,
                "event_id": event_id,
                "date": datetime.strptime(date, "%B %d, %Y").strftime("%Y-%m-%d"),
                "type": type,
                "location": location,
            }
            event_list.append(event)
            i += 1
            if i == last:
                break
    # sort by date to maintain a consistent order of event ids between the initial scraping and the following ones.
    event_list = sorted(event_list, key=lambda k: k["date"])
    return save_events(event_list)
