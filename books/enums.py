from django.db import models


class Cover(models.IntegerChoices):
    HARD = 1
    SOFT = 2
