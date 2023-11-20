from django.db import models
from django.contrib.auth.models import User


class Contest(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("live", "Live"),
        ("closed", "Closed"),
    ]
    event = models.ForeignKey("ufcscraper.Event", on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="open")

    def __str__(self):
        return f"{self.event.name} ({self.status})"


class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)  # Updated when the contest is finished

    class Meta:
        unique_together = (
            "user",
            "contest",
        )  # Ensures one prediction per user per contest

    def __str__(self):
        return f"{self.user.username} - {self.contest}"


class Prognostic(models.Model):
    METHOD_CHOICES = [
        ("decision", "Decision"),
        ("ko_tko", "KO/TKO"),
        ("submission", "Submission"),
        ("cnc", "CNC (Could not continue)"),  # Cancelled/No Contest
    ]

    BONUS_CHOICES = [
        ("fight", "Fight of the Night"),
        ("perf", "Performance of the Night"),
        ("ko", "KO of the Night"),
        ("submission", "Submission of the Night"),
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

    def save(self, *args, **kwargs):
        if self.is_draw:
            self.fight_result = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.prediction.user.username} - {self.fight} - {self.prediction.contest}"
