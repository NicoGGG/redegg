from celery import shared_task
from redegg.utils import refresh_global_leaderboard_materialized_view
from redegg.models import Prediction


@shared_task(
    retry_kwargs={"max_retries": 3},
)
def refresh_global_leaderboard():
    refresh_global_leaderboard_materialized_view()


@shared_task(
    retry_kwargs={"max_retries": 3},
)
def calculate_rank(contest_id):
    """
    Calculate the rank for the prediction.
    """
    predictions = Prediction.objects.filter(contest_id=contest_id).order_by("-score")
    for rank, prediction in enumerate(predictions, start=1):
        prediction.rank = rank
    Prediction.objects.bulk_update(predictions, ["rank"])
