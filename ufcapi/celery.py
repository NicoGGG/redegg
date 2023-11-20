import os
from celery import Celery
from celery.schedules import crontab  # scheduler

# default django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ufcapi.settings")
app = Celery("ufcapi")
app.conf.timezone = "UTC"  # type: ignore
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# # scheduled task execution
# app.conf.beat_schedule = {
#     "scraping-ufc-events": {
#         "task": "ufcscraper.tasks.scrape_all_ufc_events",
#         "schedule": crontab("20", "6"),
#     },
#     "scraping-ufc-fighters": {
#         "task": "ufcscraper.tasks.scrape_all_ufc_fighters",
#         "schedule": crontab("30", "4"),
#     },
#     "scraping-last-ufc-event": {
#         "task": "ufcscraper.tasks.scrape_upcoming_ufc_event",
#         "schedule": crontab("50", "10"),
#     },
# }
