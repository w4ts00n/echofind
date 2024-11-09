from django.db import models


class Record(models.Model):
    mp4name = models.CharField(max_length=255)
    text = models.TextField()
