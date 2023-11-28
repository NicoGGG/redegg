from django.core.management.base import BaseCommand
from redegg.utils import refresh_global_leaderboard_materialized_view


class Command(BaseCommand):
    help = "Refresh the global_leaderboard Materialized View"

    def handle(self, *args, **kwargs):
        refresh_global_leaderboard_materialized_view()
        self.stdout.write(self.style.SUCCESS("Success"))
