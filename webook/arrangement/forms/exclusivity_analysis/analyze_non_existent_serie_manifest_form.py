import re

from django import forms

from webook.arrangement.models import PlanManifest


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

    def as_plan_manifest(self):
        plan_manifest = PlanManifest()
        plan_manifest.pattern = self.cleaned_data["pattern"]
        plan_manifest.patternRoutine = self.cleaned_data["patternRoutine"]
        plan_manifest.recurrence_strategy = self.cleaned_data["timeAreaMethod"]
        plan_manifest.start_date = self.cleaned_data["startDate"]
        plan_manifest.start_time = self.cleaned_data["startTime"]
        plan_manifest.end_time = self.cleaned_data["endTime"]
        plan_manifest.ticket_code = self.cleaned_data["ticketCode"]
        plan_manifest.expected_visitors = self.cleaned_data["expectedVisitors"]
        plan_manifest.title = self.cleaned_data["title"]
        plan_manifest.title_en = self.cleaned_data["title_en"]
        plan_manifest.rooms.set(self.cleaned_data["rooms"])
        plan_manifest.people.set(self.cleaned_data["people"])
        plan_manifest.display_layouts.set(self.cleaned_data["display_layouts"])
        plan_manifest.interval = self.cleaned_data["interval"]
        plan_manifest.day_of_month = self.cleaned_data["day_of_month"]
        plan_manifest.arbitrator = self.cleaned_data["arbitrator"]
        plan_manifest.day_of_week = self.cleaned_data["day_of_week"]
        plan_manifest.month = self.cleaned_data["month"]
        plan_manifest.stop_within = self.cleaned_data["stopWithin"]
        plan_manifest.stop_after_x_occurences = self.cleaned_data["stopAfterXInstances"]
        plan_manifest.project_x_months_into_future = self.cleaned_data["projectionDistanceInMonths"]
        plan_manifest.monday = self.cleaned_data["monday"]
        plan_manifest.tuesday = self.cleaned_data["tuesday"]
        plan_manifest.wednesday = self.cleaned_data["wednesday"]
        plan_manifest.thursday = self.cleaned_data["thursday"]
        plan_manifest.friday = self.cleaned_data["friday"]
        plan_manifest.saturday = self.cleaned_data["saturday"]
        plan_manifest.sunday = self.cleaned_data["sunday"]
        return plan_manifest


