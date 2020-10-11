"""Polls Views module"""
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .models import Statement, Tag, TagAssociation


class IndexView(generic.ListView):
    template_name = 'chat/index.html'
    context_object_name = 'statements'

    def get_queryset(self):
        """
        Return statements from db
        """
        return Statement.objects.all()


class DetailView(generic.DetailView):
    model = Statement
    template_name = 'chat/detail.html'
