from django.db import connection


def refresh_global_leaderboard_materialized_view():
    with connection.cursor() as cursor:
        cursor.execute("REFRESH MATERIALIZED VIEW redegg_global_leaderboard")
