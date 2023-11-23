from django.db import models
from django.utils import timezone

# Create your models here.


class Event(models.Model):
    TYPE_CHOICES = [
        ("UFC", "UFC"),
        ("Fight Night", "Fight Night"),
        # Add more types as needed
    ]

    location = models.CharField(max_length=100)
    date = models.DateField(default=timezone.now)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    link = models.CharField(max_length=500)
    event_id = models.CharField(max_length=64, unique=True)
    upcoming = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Fighter(models.Model):
    STANCE_CHOICES = [
        ("Orthodox", "Orthodox"),
        ("Southpaw", "Southpaw"),
        # Add more stances as needed
    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    nickname = models.CharField(max_length=50, blank=True, null=True)
    height = models.CharField(max_length=8, blank=True, null=True)
    weight = models.CharField(max_length=20, blank=True, null=True)
    reach = models.CharField(max_length=20, blank=True, null=True)
    stance = models.CharField(
        max_length=20, choices=STANCE_CHOICES, blank=True, null=True
    )
    belt = models.BooleanField(default=False)
    win = models.IntegerField()
    loss = models.IntegerField()
    draw = models.IntegerField()
    link = models.CharField(max_length=500)
    fighter_id = models.CharField(max_length=64, unique=True)
    photo_url = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def to_dict(self):
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "nickname": self.nickname,
            "height": self.height,
            "weight": self.weight,
            "reach": self.reach,
            "stance": self.stance,
            "belt": self.belt,
            "win": self.win,
            "loss": self.loss,
            "draw": self.draw,
            "link": self.link,
            "fighter_id": self.fighter_id,
            "photo_url": self.photo_url,
        }

    def full_name(self):
        if self.nickname:
            return f'{self.first_name} "{self.nickname}" {self.last_name}'
        else:
            return f"{self.first_name} {self.last_name}"

    def record(self):
        return f"{self.win}-{self.loss}-{self.draw}"


class Fight(models.Model):
    WIN_LOSE_CHOICES = [
        ("W", "Win"),
        ("L", "Loss"),
        ("NC", "No Contest"),
        ("DRAW", "Draw"),
        # Add more types as needed
    ]

    WEIGHT_CLASS_CHOICES = [
        ("Super Heavyweight", "Super Heavyweight"),
        ("Heavyweight", "Heavyweight"),
        ("Light Heavyweight", "Light Heavyweight"),
        ("Middleweight", "Middleweight"),
        ("Welterweight", "Welterweight"),
        ("Lightweight", "Lightweight"),
        ("Featherweight", "Featherweight"),
        ("Bantamweight", "Bantamweight"),
        ("Flyweight", "Flyweight"),
        ("Women's Featherweight", "Women's Featherweight"),
        ("Women's Bantamweight", "Women's Bantamweight"),
        ("Women's Flyweight", "Women's Flyweight"),
        ("Women's Strawweight", "Women's Strawweight"),
        ("Catch Weight", "Catch Weight"),
        ("Open Weight", "Open Weight")
        # Add more weight classes as needed
    ]

    METHOD_CHOICES = [
        ("U-DEC", "Unanimous Decision"),
        ("S-DEC", "Split Decision"),
        ("M-DEC", "Majority Decision"),
        ("KO/TKO", "Knockout/Technical Knockout"),
        ("CNC", "Could Not Continue"),
        ("SUB", "Submission"),
        ("Overturned", "Overturned"),
        ("DQ", "Disqualification"),
        # Add more methods as needed
    ]

    BONUS_CHOICES = [
        ("fight", "Fight of the Night"),
        ("perf", "Performance of the Night"),
        ("ko", "Knockout of the Night"),
        ("sub", "Submission of the Night"),
        # Add more bonuses as needed
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    fight_id = models.CharField(max_length=64, unique=True)
    position = models.IntegerField(null=True)  # Position on the card
    link = models.CharField(max_length=500)
    fighter_one = models.ForeignKey(
        Fighter, on_delete=models.CASCADE, related_name="fighter1"
    )
    fighter_two = models.ForeignKey(
        Fighter, on_delete=models.CASCADE, related_name="fighter2"
    )
    wl_fighter_one = models.CharField(
        max_length=4, choices=WIN_LOSE_CHOICES, blank=True, null=True
    )
    wl_fighter_two = models.CharField(
        max_length=4, choices=WIN_LOSE_CHOICES, blank=True, null=True
    )
    winner = models.ForeignKey(
        Fighter, on_delete=models.CASCADE, related_name="winner", blank=True, null=True
    )
    weight_class = models.CharField(max_length=50, choices=WEIGHT_CLASS_CHOICES)
    belt = models.BooleanField(default=False)
    method = models.CharField(
        null=True, blank=True, max_length=20, choices=METHOD_CHOICES
    )
    round = models.IntegerField(null=True, blank=True)
    time = models.CharField(null=True, blank=True, max_length=5)
    bonus = models.CharField(
        max_length=20, choices=BONUS_CHOICES, blank=True, null=True
    )

    def method_code(self):
        """
        Regroup method values into: decision, ko_tko, submission, and cnc
        """
        if self.method in ["U-DEC", "S-DEC", "M-DEC"]:
            return "decision"
        elif self.method == "KO/TKO":
            return "ko_tko"
        elif self.method == "SUB":
            return "submission"
        elif self.method == "CNC":
            return "cnc"
        else:
            return None

    def fight_result(self):
        if self.wl_fighter_one == "W":
            return self.fighter_one
        elif self.wl_fighter_two == "W":
            return self.fighter_two
        elif self.wl_fighter_one == "DRAW" or self.wl_fighter_two == "DRAW":
            return "DRAW"

    def fight_info(self):
        out = f"{self.fighter_one } vs {self.fighter_two}: "
        out += f"{self.weight_class}"
        if self.belt:
            out += " Title Fight"
        else:
            out += " Bout"

        return out

    def is_main_event(self):
        return self.position == 1

    def is_co_main_event(self):
        return self.position == 2

    def is_main_card(self):
        return self.position <= 5

    def is_prelim(self):
        return self.position > 5

    def __str__(self):
        return f"{self.fighter_one} vs {self.fighter_two}"
