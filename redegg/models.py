import uuid
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from ufcscraper.models import Event


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar_url = models.URLField(blank=True, null=True)
    base_username = models.CharField(max_length=50, blank=True, null=True)
    display_username = models.CharField(max_length=50, blank=True, null=True)
    extra_data = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.display_username} - {self.user.username}"


class Contest(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("live", "Live"),
        ("closed", "Closed"),
    ]
    event = models.OneToOneField(Event, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="open")
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.event.name)
        super().save(*args, **kwargs)

    def calculate_all_predictions_scores(self):
        """
        Calculate the scores for all predictions in the contest.
        Operation is commited and will save the prognostics and predictions after calculation.
        """
        predictions = self.prediction_set.all()
        for prediction in predictions:
            prognostics = prediction.prognostic_set.all()
            for prognostic in prediction.prognostic_set.all():
                prognostic.calculate_points_and_bonus_percentage()
            Prognostic.objects.bulk_update(
                prognostics,
                [
                    "points",
                    "bonus_percentage",
                    "fight_result_won",
                    "method_won",
                    "bonus_won",
                ],
            )
            prediction.calculate_score()
        Prediction.objects.bulk_update(predictions, ["score"])

    def calculate_all_predictions_rank(self):
        """
        Calculate the rank for the predictions of a contest.
        """
        predictions = Prediction.objects.filter(contest_id=self.id).order_by("-score")
        for rank, prediction in enumerate(predictions, start=1):
            prediction.rank = rank
        Prediction.objects.bulk_update(predictions, ["rank"])

    def __str__(self):
        return f"{self.event.name} ({self.status})"


class Prediction(models.Model):
    # Unique anon identifier
    prediction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)  # Raw points
    bonus_modifier = models.IntegerField(default=0)  # Bonus modifier (in percentage)
    score = models.IntegerField(
        default=0
    )  # Total score after points and bonus modifier
    rank = models.IntegerField(default=0)  # Rank in the contest

    def calculate_points(self):
        """
        Calculate the points for the prediction.
        """
        prognostics = self.prognostic_set.all()
        points = 0
        for prognostic in prognostics:
            points += prognostic.points
        self.points = points

    def calculate_bonus_modifier(self):
        """
        Calculate the bonus modifier for the prediction.
        """
        prognostics = self.prognostic_set.all()
        bonus_modifier = 0
        prognostics_won = 0
        for prognostic in prognostics:
            bonus_modifier += prognostic.bonus_percentage
            if prognostic.fight_result_won:
                prognostics_won += 1
        if prognostics_won > 1:
            bonus_modifier += 10 * (prognostics_won - 1)
        self.bonus_modifier = bonus_modifier if bonus_modifier > 0 else 0

    def calculate_score(self):
        """
        Calculate the score for the prediction.
        """
        self.calculate_points()
        self.points = self.points if self.points > 0 else 0
        self.calculate_bonus_modifier()
        self.score = self.points + int(self.points * self.bonus_modifier / 100)

    class Meta:
        unique_together = (
            "user",
            "contest",
        )  # Ensures one prediction per user per contest

    def save(self, *args, **kwargs):
        if not self.prediction_id:
            self.prediction_id = uuid.uuid4()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.contest}"


class Prognostic(models.Model):
    METHOD_CHOICES = [
        ("decision", "Decision"),
        ("ko_tko", "KO/TKO"),
        ("submission", "Submission"),
        ("cnc", "CNC"),
    ]

    BONUS_CHOICES = [
        ("fight", "Fight of the Night"),
        ("perf", "Performance of the Night"),
        ("ko", "KO of the Night"),
        ("sub", "Submission of the Night"),
    ]

    prediction = models.ForeignKey(Prediction, on_delete=models.CASCADE)
    fight = models.ForeignKey("ufcscraper.Fight", on_delete=models.CASCADE)
    fight_result = models.ForeignKey(
        "ufcscraper.Fighter", on_delete=models.SET_NULL, null=True, blank=True
    )
    is_draw = models.BooleanField(default=False)
    method = models.CharField(
        max_length=10, choices=METHOD_CHOICES, blank=True, null=True
    )
    bonus = models.CharField(
        max_length=20, choices=BONUS_CHOICES, blank=True, null=True
    )
    points = models.IntegerField(default=0)
    fight_result_won = models.BooleanField(default=False)
    bonus_percentage = models.IntegerField(default=0)
    method_won = models.BooleanField(default=False)
    bonus_won = models.BooleanField(default=False)

    def calculate_points(self):
        """
        Calculate the points and bonus percentage for the prognostic.
        """
        fight = self.fight
        fight_points = 0
        points = 0
        if fight.is_main_event():
            fight_points = 100
        elif fight.is_co_main_event():
            fight_points = 50
        elif fight.is_main_card():
            fight_points = 20
        else:
            fight_points = 10
        if self.fight_result and self.fight_result == fight.winner:
            self.fight_result_won = True
            points = fight_points
        elif not self.fight_result and (self.is_draw and fight.is_draw_or_no_contest()):
            self.fight_result_won = True
            points = fight_points
        else:
            self.fight_result_won = False
            if fight.is_prelim():
                points = -10
        self.points = points

    def calculate_bonus_percentage(self):
        """
        Calculate the bonus percentage for the prognostic.
        """
        bonus_percentage = 0
        if self.method and self.method == self.fight.method_code():
            self.method_won = True
            bonus_percentage += 30
        elif self.method:
            self.method_won = False
            bonus_percentage -= 30
        if self.bonus and self.bonus == self.fight.bonus:
            self.bonus_won = True
            bonus_percentage += 50
        elif self.bonus:
            self.bonus_won = False
            bonus_percentage -= 50
        self.bonus_percentage = bonus_percentage

    def calculate_points_and_bonus_percentage(self):
        """
        Calculate the points and bonus percentage for the prognostic.
        """
        self.calculate_points()
        self.calculate_bonus_percentage()

    def save(self, *args, **kwargs):
        if self.is_draw:
            self.fight_result = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.prediction.user.username} - {self.fight} - {self.prediction.contest}"


class GlobalLeaderboard(models.Model):
    year = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    total_score = models.IntegerField()
    rank = models.IntegerField()

    class Meta:
        managed = False
        db_table = "redegg_global_leaderboard"
