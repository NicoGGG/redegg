import os
from celery import Celery
from celery.schedules import crontab  # scheduler

# default django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ufcapi.settings")
app = Celery("ufcapi")
app.conf.timezone = "UTC"  # type: ignore
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# scheduled task execution
if os.getenv("CELERY_CRON_ENABLED", "False").lower() in ("true", "1", "t"):
    app.conf.beat_schedule = {
        # Update upcoming UFC event daily at 6:20 AM UTC in case of any changes in the event
        "updating-next-ufc-event-daily": {
            "task": "ufcscraper.tasks.scrape_all_ufc_events",
            "args": (1,),
            "schedule": crontab("20", "6"),
        },
        # Update all fighters once a month at 4:30 AM UTC to keep the data up to date
        "scraping-ufc-fighters": {
            "task": "ufcscraper.tasks.scrape_all_ufc_fighters",
            "schedule": crontab("30", "4", day_of_month="1"),
        },
        # Update last 2 UFC every 5 minutes during the time an event is usually live on Saturday and Sunday
        "scraping-last-ufc-event": {
            "task": "ufcscraper.tasks.scrape_all_ufc_events",
            "args": (2,),
            "schedule": crontab("0-59/5", "20-23,0-6", day_of_week="sat,sun"),
        },
        # Refresh the global leaderboard every monday at 10:00 AM UTC, when the sunday event is over
        "refreshing-global-leaderboard": {
            "task": "redegg.tasks.refresh_global_leaderboard",
            "schedule": crontab("0", "10", day_of_week="mon"),
        },
    }
