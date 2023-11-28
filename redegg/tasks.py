from celery import shared_task
from redegg.utils import refresh_global_leaderboard_materialized_view


@shared_task(
    retry_kwargs={"max_retries": 3},
)
def refresh_global_leaderboard():
    refresh_global_leaderboard_materialized_view()
