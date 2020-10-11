"""Models module"""
import datetime
from django.db import models
from django.utils import timezone


class Statement(models.Model):
    statement_text = models.CharField(max_length=255)
    search_text = models.CharField(max_length=255)
    search_text.short_description = 'search text'
    conversation = models.CharField(max_length=32)
    created_at = models.DateTimeField('created at')
    in_response_to = models.CharField(max_length=255)
    in_response_to.short_description = 'response to'
    search_in_response_to = models.CharField(max_length=255)
    search_in_response_to.short_description = 'search in response to'
    persona = models.CharField(max_length=50)

    def __str__(self):
        return str(self.statement_text)


class Tag(models.Model):
    name = models.CharField(max_length=50)


class TagAssociation(models.Model):
    statement = models.ForeignKey(Statement, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
