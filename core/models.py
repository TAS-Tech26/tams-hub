# models.py


from django.db import models


class School(models.Model):

    name = models.CharField(max_length = 255, unique = True)


class TamsTeam(models.Model):

    team_code = models.CharField(max_length = 10, unique = True, db_index = True)
    name = models.CharField(max_length = 255)
    school = models.ForeignKey(School, on_delete = models.CASCADE)
    event_name = models.CharField(max_length = 255)

class EventStanding(models.Model):

    event_name = models.CharField(max_length = 255, db_index = True)
    rank = models.IntegerField()
    final_score_or_assets = models.CharField(max_length = 255) # B2B assets won or Kahoot score

    team = models.ForeignKey(TamsTeam, on_delete = models.CASCADE)

    class Meta:

        ordering = ['rank']