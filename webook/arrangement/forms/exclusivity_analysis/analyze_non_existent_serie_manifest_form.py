import re

from django import forms


class AnalyzeNonExistentSerieManifestForm(forms.Form):
    pattern = forms.CharField(max_length=255)
    patternRoutine = forms.CharField(max_length=255)
    timeAreaMethod = forms.CharField(max_length=255)
    startDate = forms.DateField()
    startTime = forms.TimeField()
    endTime = forms.TimeField()
    ticketCode = forms.CharField(max_length=255, required=False)
    expectedVisitors = forms.IntegerField(min_value=0)
    title = forms.CharField(max_length=512)
    title_en = forms.CharField(max_length=512, required=False)
    rooms = forms.CharField(max_length=1024, required=False)
    people = forms.CharField(max_length=1024, required=False)
    display_layouts = forms.CharField(max_length=1024, required=False)
    interval = forms.IntegerField(required=False)
    day_of_month = forms.IntegerField(required=False)
    arbitrator = forms.IntegerField(required=False)
    day_of_week = forms.IntegerField(required=False)
    month = forms.IntegerField(required=False)
    stopWithin = forms.DateField(required=False)
    stopAfterXInstances = forms.IntegerField(required=False)
    projectionDistanceInMonths = forms.IntegerField(required=False)

    monday = forms.BooleanField(required=False)
    tuesday = forms.BooleanField(required=False)
    wednesday = forms.BooleanField(required=False)
    thursday = forms.BooleanField(required=False)
    friday = forms.BooleanField(required=False)
    saturday = forms.BooleanField(required=False)
    sunday = forms.BooleanField(required=False)
