from django.db import models


class Cover(models.IntegerChoices):
    SOFT = 1
    HARD = 2
