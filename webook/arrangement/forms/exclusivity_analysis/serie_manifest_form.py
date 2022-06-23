from django import forms
from django.http import JsonResponse

from webook.arrangement.models import Arrangement, Event, EventSerie, Person, PlanManifest, Room
from webook.screenshow.models import DisplayLayout
from webook.utils.collision_analysis import analyze_collisions
from webook.utils.serie_calculator import calculate_serie


class SerieManifestForm(forms.Form):
    """ Form representing a serie manifest, tightly related to the model PlanManifest """
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
    rooms = forms.ModelMultipleChoiceField(queryset=Room.objects.all(), required=False)
    people = forms.CharField(max_length=5000, required=False)
    display_layouts = forms.CharField(max_length=5000, required=False)
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
        """Convert the SerieManifestForm to a valid PlanManifest """
        plan_manifest = PlanManifest()
        plan_manifest.pattern = self.cleaned_data["pattern"]
        plan_manifest.pattern_strategy = self.cleaned_data["patternRoutine"]
        plan_manifest.recurrence_strategy = self.cleaned_data["timeAreaMethod"]
        plan_manifest.start_date = self.cleaned_data["startDate"]
        plan_manifest.start_time = self.cleaned_data["startTime"]
        plan_manifest.end_time = self.cleaned_data["endTime"]
        plan_manifest.ticket_code = self.cleaned_data["ticketCode"]
        plan_manifest.expected_visitors = self.cleaned_data["expectedVisitors"]
        plan_manifest.title = self.cleaned_data["title"]
        plan_manifest.title_en = self.cleaned_data["title_en"]

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
        
        plan_manifest.save()

        parse_comma_sep_string = lambda comma_sep_str: [int(x) for x in comma_sep_str.split(",") if x] if comma_sep_str else []

        plan_manifest.rooms.set(parse_comma_sep_string(self.cleaned_data["rooms"]))
        plan_manifest.people.set(parse_comma_sep_string(self.cleaned_data["people"]))
        plan_manifest.display_layouts.set(parse_comma_sep_string(self.cleaned_data["display_layouts"]))

        plan_manifest.save()

        return plan_manifest


class CreateSerieForm(SerieManifestForm):
    arrangementPk = forms.IntegerField()
    predecessorSerie = forms.IntegerField(required=False)

    def save(self, form, *args, **kwargs) -> JsonResponse:
        manifest = form.as_plan_manifest()
        calculated_serie = calculate_serie(manifest)

        for ev in calculated_serie:
            ev.rooms = [int(room.id) for room in manifest.rooms.all()]

        _ = analyze_collisions(calculated_serie)

        serie = EventSerie()
        serie.arrangement = Arrangement.objects.get(id=form.cleaned_data["arrangementPk"])
        serie.serie_plan_manifest = manifest
        serie.save()

        pk_of_preceding_event_serie = form.cleaned_data["predecessorSerie"];
        if pk_of_preceding_event_serie:
            predecessor_event_serie = EventSerie.objects.get(id=pk_of_preceding_event_serie)
            predecessor_event_serie.archive(kwargs["user"].person)

        room_ids = [room.id for room in manifest.rooms.all()]
        people_ids = [person.id for person in manifest.people.all()]
        display_layout_ids = [display_layout.id for display_layout in manifest.display_layouts.all()]

        create_events = []

        for ev in calculated_serie:
            if ev.is_collision:
                continue
            
            event = Event()
            event.arrangement = serie.arrangement
            event.title = manifest.title
            event.title_en = manifest.title_en
            event.ticket_code = manifest.ticket_code
            event.expected_visitors = manifest.expected_visitors
            event.serie = serie
            event.start = ev.start
            event.end = ev.end

            create_events.append(event)

        created_events = Event.objects.bulk_create(create_events)
        
        room_throughs = []
        people_throughs = []
        display_layout_throughs = []

        for event in created_events:
            room_throughs = room_throughs + [Event.rooms.through(event_id=event.id, room_id=room_id) for room_id in room_ids if room_ids]
            people_throughs = people_throughs + [Event.people.through(event_id=event.id, person_id=person_id) for person_id in people_ids if people_ids]
            display_layout_throughs = display_layout_throughs + [Event.display_layouts.through(event_id=event.id, displaylayout_id=display_layout_id) 
                                                                 for display_layout_id in display_layout_ids if display_layout_ids]

        Event.rooms.through.objects.bulk_create(room_throughs)
        Event.people.through.objects.bulk_create(people_throughs)
        Event.display_layouts.through.objects.bulk_create(display_layout_throughs)
