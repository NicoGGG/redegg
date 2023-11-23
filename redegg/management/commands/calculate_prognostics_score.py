from django.core.management.base import BaseCommand

from redegg.models import Contest


class Command(BaseCommand):
    help = "Calculate the prognostics score for a contest"

    def add_arguments(self, parser):
        parser.add_argument("contest_id", type=int, help="The Django contest ID")

    def handle(self, *args, **kwargs):
        contest_id = kwargs["contest_id"]
        self.stdout.write(
            self.style.NOTICE(f"Calculating prognostics score for contest {contest_id}")
        )
        try:
            # Fetch the contest.
            contest = Contest.objects.get(id=contest_id)

            # Fetch the predictions and prognostics of all users for the contest.
            predictions = contest.prediction_set.all()

            # Fetch all the fights from the event of the contest.
            fights = contest.event.fight_set.all()

            for prediction in predictions:
                prognostics = prediction.prognostic_set.all()
                # Fight / Prognostic pairs.
                prognostic_dict = {
                    prognostic.fight.id: prognostic
                    for prognostic in prognostics
                    if prognostic is not None
                }
                fight_prognostic_pairs = [
                    (fight, prognostic_dict.get(fight.id)) for fight in fights
                ]
                total_score = 0
                total_bonus_percentage = 0
                # Calculate the score for each prognostic.
                for fight, prognostic in fight_prognostic_pairs:
                    if prognostic:
                        """
                        Calculate the score for the prognostic and save.
                        A prognostic gets
                        - 100 points if the fight result is correct for the main event.
                        - 50 points for the co-main event.
                        - 20 points for the rest of the fights of the main card.
                        - 10 points for the prelim fights.

                        If a prognostic has a method, it gets 30% raw bonus points if the method is correct.
                        If a prognostic has a bonus, it gets 50% raw bonus points if the bonus is correct.
                        """
                        if fight.is_main_event():
                            fight_points = 100
                        elif fight.is_co_main_event():
                            fight_points = 50
                        elif fight.is_main_card():
                            fight_points = 20
                        else:
                            fight_points = 10
                        score = 0
                        method_percentage = 0
                        bonus_percentage = 0
                        if (
                            prognostic.fight_result
                            and prognostic.fight_result == fight.winner
                        ):
                            prognostic.fight_result_won = True
                            score = fight_points
                            total_score += score
                        elif not prognostic.fight_result and (
                            prognostic.is_draw
                            and fight.wl_fighter_one == "DRAW"
                            or prognostic.is_draw
                            and fight.wl_fighter_one == "NC"
                        ):
                            prognostic.fight_result_won = True
                            score = fight_points
                            total_score += score
                        else:
                            prognostic.fight_result_won = False
                        if prognostic.method == fight.method_code():
                            prognostic.method_won = True
                            method_percentage = 30
                            total_bonus_percentage += 30
                        if prognostic.bonus == fight.bonus:
                            prognostic.bonus_won = True
                            total_bonus_percentage += 50
                            bonus_percentage = 50
                        prognostic.points = score
                        prognostic.bonus_percentage = (
                            method_percentage + bonus_percentage
                        )
                        prognostic.save()
                # Calculate the score for the prediction.
                prediction.score = total_score + int(
                    total_score * total_bonus_percentage / 100
                )

                # Save the prediction.
                prediction.save()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
        else:
            self.stdout.write(self.style.SUCCESS("Success"))
