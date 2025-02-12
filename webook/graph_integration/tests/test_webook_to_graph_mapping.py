from django.test import TestCase
from webook.arrangement.models import (
    Arrangement,
    Location,
    EventSerie,
    Audience,
    Room,
    Person,
    Event as WebookEvent,
    PlanManifest as WebookPlanManifest,
)
import webook.graph_integration.routines.mapping.repeating_event_mapping as rem
from msgraph.generated.models.day_of_week import DayOfWeek
from typing import List
from datetime import date, time, datetime, timedelta
from msgraph.generated.models.week_index import WeekIndex
from msgraph.generated.models.recurrence_pattern import RecurrencePattern
from msgraph.generated.models.recurrence_range import RecurrenceRange
from msgraph.generated.models.recurrence_pattern_type import RecurrencePatternType
from msgraph.generated.models.recurrence_range_type import RecurrenceRangeType
from msgraph.generated.models.body_type import BodyType


class EventMappingTestCase(TestCase):
    def test_event_mapping(self):
        person_a = Person.objects.create(
            first_name="Person",
            last_name="A",
            social_provider_email="email@test.com",
            social_provider_id="mock_social_provider_id",
            calendar_sync_enabled=True,
        )

        def_audience = Audience.objects.create(name="Default Audience")
        location = Location.objects.create(name="Default Location")
        arrangement = Arrangement.objects.create(
            name="Test Arrangement",
            audience=def_audience,
            location=location,
        )

        room_a = Room.objects.create(name="Room A", max_capacity=100, location=location)
        room_b = Room.objects.create(name="Room B", max_capacity=100, location=location)

        event = WebookEvent.objects.create(
            arrangement=arrangement,
            title="Test Event",
            start=datetime(2021, 1, 1, 10, 0),
            end=datetime(2021, 1, 1, 11, 0),
        )
        event.rooms.add(room_a)
        event.rooms.add(room_b)
        event.people.add(person_a)

        graph_event = rem.map_event_to_graph_event(event)

        self.assertEqual(graph_event.subject, "Test Event")
        self.assertEqual(graph_event.body.content, "Test Event")
        self.assertEqual(graph_event.body.content_type, BodyType.Html)
        self.assertEqual(graph_event.start.date_time, "2021-01-01T10:00:00")
        self.assertEqual(graph_event.end.date_time, "2021-01-01T11:00:00")
        self.assertEqual(
            graph_event.location.display_name, "Default Location (Room A, Room B)"
        )
        self.assertEqual(len(graph_event.attendees), 1)
        self.assertEqual(
            graph_event.attendees[0].email_address.address,
            person_a.social_provider_email,
        )
        self.assertEqual(graph_event.attendees[0].email_address.name, "Person A")
        self.assertEqual(graph_event.attendees[0].type, "required")

        self.assertEqual(graph_event.allow_new_time_proposals, False)


class RepeatingEventMappingTestCase(TestCase):
    def test_weekday_mapper(self):
        """Test that the weekday mapper correctly maps the manifest
        to a list of DayOfWeek."""
        manifest = WebookPlanManifest.objects.create(
            start_date=date(2021, 1, 1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=False,
            friday=False,
            saturday=False,
            sunday=False,
        )

        dow_list: List[DayOfWeek] = rem._weekday_mapper(manifest)

        self.assertEqual(type(dow_list), list)
        self.assertEqual(len(dow_list), 3)
        self.assertEqual(dow_list[0], DayOfWeek.Monday)
        self.assertEqual(dow_list[1], DayOfWeek.Tuesday)
        self.assertEqual(dow_list[2], DayOfWeek.Wednesday)

    def test_weekday_mapper_no_days(self):
        """Test that the weekday mapper correctly maps the manifest
        to an empty list of DayOfWeek."""
        manifest = WebookPlanManifest.objects.create(
            start_date=date(2021, 1, 1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            monday=False,
            tuesday=False,
            wednesday=False,
            thursday=False,
            friday=False,
            saturday=False,
            sunday=False,
        )

        dow_list: List[DayOfWeek] = rem._weekday_mapper(manifest)

        self.assertEqual(type(dow_list), list)
        self.assertEqual(len(dow_list), 0)

    def test_arbitrator_mapper(self):
        manifest = WebookPlanManifest.objects.create(
            start_date=date(2021, 1, 1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            arbitrator="0",
        )

        week_index: WeekIndex = rem._arbitrator_mapper(manifest)
        self.assertEqual(week_index, WeekIndex.First)

        manifest.arbitrator = "1"
        week_index: WeekIndex = rem._arbitrator_mapper(manifest)
        self.assertEqual(week_index, WeekIndex.Second)

        manifest.arbitrator = "2"
        week_index: WeekIndex = rem._arbitrator_mapper(manifest)
        self.assertEqual(week_index, WeekIndex.Third)

        manifest.arbitrator = "3"
        week_index: WeekIndex = rem._arbitrator_mapper(manifest)
        self.assertEqual(week_index, WeekIndex.Fourth)

        manifest.arbitrator = "4"
        week_index: WeekIndex = rem._arbitrator_mapper(manifest)
        self.assertEqual(week_index, WeekIndex.Last)

    def test_arbitrator_mapper_invalid(self):
        manifest = WebookPlanManifest.objects.create(
            start_date=date(2021, 1, 1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            arbitrator="5",
        )

        with self.assertRaises(ValueError):
            rem._arbitrator_mapper(manifest)

    def test_map_every_weekday_pattern_to_graph_recurrence_pattern(self):
        """Test that the every weekday pattern is correctly mapped to a Graph RecurrencePattern."""
        manifest = WebookPlanManifest.objects.create(
            start_date=date(2021, 1, 1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            pattern_strategy="daily__every_weekday",
        )

        rp: RecurrencePattern = rem._map_every_weekday_pattern(manifest)

        self.assertEqual(rp.type, RecurrencePatternType.Weekly)
        # since we haven't set an interval, we expect it to be 1
        self.assertEqual(rp.interval, 1)
        self.assertEqual(
            rp.days_of_week,
            [
                DayOfWeek.Monday,
                DayOfWeek.Tuesday,
                DayOfWeek.Wednesday,
                DayOfWeek.Thursday,
                DayOfWeek.Friday,
            ],
        )
        self.assertEqual(rp.first_day_of_week, DayOfWeek.Monday)

        manifest.interval = 2
        manifest.sunday = True
        rp: RecurrencePattern = rem._map_every_weekday_pattern(manifest)

        self.assertEqual(rp.interval, 2)
        # assert that sunday is ignored
        self.assertEqual(
            rp.days_of_week,
            [
                DayOfWeek.Monday,
                DayOfWeek.Tuesday,
                DayOfWeek.Wednesday,
                DayOfWeek.Thursday,
                DayOfWeek.Friday,
            ],
        )

    def test_map_weekly_pattern_to_graph_recurrence_pattern(self):
        """Test that the weekly pattern is correctly mapped to a Graph RecurrencePattern."""
        manifest = WebookPlanManifest.objects.create(
            start_date=date(2021, 1, 1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            pattern_strategy="weekly__standard",
            monday=True,
            wednesday=True,
        )

        rp: RecurrencePattern = rem._map_weekly_pattern(manifest)

        self.assertEqual(rp.type, RecurrencePatternType.Weekly)
        self.assertEqual(rp.interval, 1)
        self.assertEqual(
            rp.days_of_week,
            [
                DayOfWeek.Monday,
                DayOfWeek.Wednesday,
            ],
        )
        self.assertEqual(rp.first_day_of_week, DayOfWeek.Monday)

        manifest.interval = 2
        rp: RecurrencePattern = rem._map_weekly_pattern(manifest)

        self.assertEqual(rp.interval, 2)

    def test_map_weekly_pattern_to_graph_raises_if_no_days(self):
        """Test that the weekly pattern raises a ValueError if no days are selected."""
        manifest = WebookPlanManifest.objects.create(
            start_date=date(2021, 1, 1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            pattern_strategy="weekly__standard",
        )

        with self.assertRaises(ValueError):
            rem._map_weekly_pattern(manifest)

    def test_map_every_x_day_every_y_month_pattern_to_graph_recurrence_pattern(self):
        """Test that the every x day every y month pattern is correctly mapped to a Graph RecurrencePattern."""
        manifest = WebookPlanManifest.objects.create(
            start_date=date(2021, 1, 1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            pattern_strategy="month__every_x_day_every_y_month",
            interval=2,
            day_of_month=15,
        )

        rp: RecurrencePattern = rem._map_every_x_day_every_y_month_pattern(manifest)

        self.assertEqual(rp.type, RecurrencePatternType.AbsoluteMonthly)
        self.assertEqual(rp.interval, 2)
        self.assertEqual(rp.day_of_month, 15)

    def test_map_every_x_day_every_y_month_pattern_to_graph_raises_if_no_day_of_month(
        self,
    ):
        manifest = WebookPlanManifest.objects.create(
            start_date=date(2021, 1, 1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            pattern_strategy="month__every_x_day_every_y_month",
            interval=2,
        )

        with self.assertRaises(ValueError):
            rem._map_every_x_day_every_y_month_pattern(manifest)

    def test_map_every_arbitrary_date_of_month_pattern_to_graph(self):
        """Test that the every arbitrary date of month pattern is correctly mapped to a Graph RecurrencePattern."""
        manifest = WebookPlanManifest.objects.create(
            start_date=date(2021, 1, 1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            pattern_strategy="month__every_arbitrary_date_of_month",
            arbitrator="0",
            monday=True,
        )
        # Effectively saying; every first monday every 1 months
        # This is a relative monthly pattern

        rp: RecurrencePattern = rem._map_every_arbitrary_date_of_month_pattern(manifest)

        self.assertEqual(rp.type, RecurrencePatternType.RelativeMonthly)
        self.assertEqual(rp.interval, 1)
        self.assertEqual(rp.index, WeekIndex.First)

    def test_map_every_arbitrary_date_of_month_pattern_to_graph_raises_if_no_arbitrator(
        self,
    ):
        manifest = WebookPlanManifest.objects.create(
            start_date=date(2021, 1, 1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            pattern_strategy="month__every_arbitrary_date_of_month",
            monday=True,
        )

        with self.assertRaises(ValueError):
            rem._map_every_arbitrary_date_of_month_pattern(manifest)

    def test_map_every_arbitrary_date_of_month_pattern_to_graph_raises_if_no_days(
        self,
    ):
        manifest = WebookPlanManifest.objects.create(
            start_date=date(2021, 1, 1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            pattern_strategy="month__every_arbitrary_date_of_month",
            arbitrator="0",
        )

        with self.assertRaises(ValueError):
            rem._map_every_arbitrary_date_of_month_pattern(manifest)

    def test_map_yearly_every_x_of_month_pattern_to_graph(self):
        """Test that the yearly every x of month pattern is correctly mapped to a Graph RecurrencePattern."""
        manifest = WebookPlanManifest.objects.create(
            start_date=date(2021, 1, 1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            pattern_strategy="year__every_x_of_month",
            month=5,
            day_of_month=15,
            interval=2,
        )

        rp: RecurrencePattern = rem._map_yearly_every_x_of_month_pattern(manifest)

        self.assertEqual(rp.type, RecurrencePatternType.AbsoluteYearly)
        self.assertEqual(rp.interval, 2)
        self.assertEqual(rp.day_of_month, 15)
        self.assertEqual(rp.month, 4)  # 0-indexed in Graph, 1 indexed in WeBook

        manifest.interval = None
        rp: RecurrencePattern = rem._map_yearly_every_x_of_month_pattern(manifest)
        self.assertEqual(rp.interval, 1)

    def test_map_yearly_every_x_of_month_pattern_to_graph_raises_if_no_month(self):
        manifest = WebookPlanManifest.objects.create(
            start_date=date(2021, 1, 1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            pattern_strategy="year__every_x_of_month",
            day_of_month=15,
            interval=2,
        )

        with self.assertRaises(ValueError):
            rem._map_yearly_every_x_of_month_pattern(manifest)

    def test_map_yearly_every_x_of_month_pattern_to_graph_raises_if_no_day_of_month(
        self,
    ):
        manifest = WebookPlanManifest.objects.create(
            start_date=date(2021, 1, 1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            pattern_strategy="year__every_x_of_month",
            month=5,
            interval=2,
        )

        with self.assertRaises(ValueError):
            rem._map_yearly_every_x_of_month_pattern(manifest)

    def test_map_every_arbitrary_weekday_in_month_pattern_to_graph(self):
        """Test that the every arbitrary weekday in month pattern is correctly mapped to a Graph RecurrencePattern."""
        manifest = WebookPlanManifest.objects.create(
            start_date=date(2021, 1, 1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            pattern_strategy="yearly__every_arbitrary_weekday_in_month",
            arbitrator="0",
            monday=True,
            month=5,
            interval=2,
        )
        # Effectively saying; every first monday in May every 2 years
        # This is a relative yearly pattern

        rp: RecurrencePattern = rem._map_every_arbitrary_weekday_in_month_pattern(
            manifest
        )

        self.assertEqual(rp.type, RecurrencePatternType.RelativeYearly)
        self.assertEqual(rp.interval, 2)
        self.assertEqual(rp.index, WeekIndex.First)
        self.assertEqual(rp.days_of_week, [DayOfWeek.Monday])

        manifest.interval = None
        rp = rem._map_every_arbitrary_weekday_in_month_pattern(manifest)
        self.assertEqual(rp.interval, 1)

    def test_map_every_arbitrary_weekday_in_month_pattern_to_graph_raises_if_no_arbitrator(
        self,
    ):
        manifest = WebookPlanManifest.objects.create(
            start_date=date(2021, 1, 1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            pattern_strategy="yearly__every_arbitrary_weekday_in_month",
            monday=True,
            month=5,
            interval=2,
        )

        with self.assertRaises(ValueError):
            rem._map_every_arbitrary_weekday_in_month_pattern(manifest)

    def test_map_every_arbitrary_weekday_in_month_pattern_to_graph_raises_if_no_days(
        self,
    ):
        manifest = WebookPlanManifest.objects.create(
            start_date=date(2021, 1, 1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            pattern_strategy="yearly__every_arbitrary_weekday_in_month",
            arbitrator="0",
            month=5,
            interval=2,
        )

        with self.assertRaises(ValueError):
            rem._map_every_arbitrary_weekday_in_month_pattern(manifest)

    def test_map_stop_within_range_to_graph_recurrence_range(self):
        manifest = WebookPlanManifest.objects.create(
            start_date=date(2021, 1, 1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            pattern_strategy="daily__every_x_day",
            interval=1,
            recurrence_strategy="StopWithin",
            stop_within=date(2021, 1, 10),
        )

        rr: RecurrenceRange = rem._map_stop_within_range(manifest)

        self.assertEqual(rr.type, RecurrenceRangeType.EndDate)
        self.assertEqual(rr.start_date.date_time, "2021-01-01")
        self.assertEqual(rr.end_date.date_time, "2021-01-10")

        # Dates stored in WeBook are in UTC
        self.assertEqual(rr.start_date.time_zone, "UTC")
        self.assertEqual(rr.end_date.time_zone, "UTC")

    def test_map_stop_after_x_occurrences_to_graph_recurrence_range(self):
        manifest = WebookPlanManifest.objects.create(
            start_date=date(2021, 1, 1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            pattern_strategy="daily__every_x_day",
            interval=1,
            recurrence_strategy="StopAfter",
            stop_after_x_occurences=10,
        )

        rr: RecurrenceRange = rem._map_stop_after_x_occurrences(manifest)

        self.assertEqual(rr.type, RecurrenceRangeType.Numbered)
        self.assertEqual(rr.start_date.date_time, "2021-01-01")
        self.assertEqual(rr.number_of_occurrences, 10)
        self.assertEqual(rr.start_date.time_zone, "UTC")

    def test_map_no_stop_date_range_to_graph_recurrence_range(self):
        manifest = WebookPlanManifest.objects.create(
            start_date=date(2021, 1, 1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            pattern_strategy="daily__every_x_day",
            interval=1,
            recurrence_strategy="NoStop",
        )

        rr: RecurrenceRange = rem._map_no_stop_date_range(manifest)

        self.assertEqual(rr.type, RecurrenceRangeType.NoEnd)
        self.assertEqual(rr.start_date.date_time, "2021-01-01")
        self.assertEqual(rr.start_date.time_zone, "UTC")

    def test_map_recurrence_range_to_graph_recurrence_range(self):
        manifest = WebookPlanManifest.objects.create(
            start_date=date(2021, 1, 1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            pattern_strategy="daily__every_x_day",
            interval=1,
            recurrence_strategy="StopWithin",
            stop_within=date(2021, 1, 10),
        )

        rr: RecurrenceRange = rem._map_recurrence_range(manifest)

        self.assertEqual(rr.type, RecurrenceRangeType.EndDate)
        self.assertEqual(rr.start_date.date_time, "2021-01-01")
        self.assertEqual(rr.end_date.date_time, "2021-01-10")
        self.assertEqual(rr.start_date.time_zone, "UTC")
        self.assertEqual(rr.end_date.time_zone, "UTC")

    def test_map_serie_to_graph_event(self):
        def_audience = Audience.objects.create(name="Default Audience")
        location = Location.objects.create(name="Default Location")
        arrangement = Arrangement.objects.create(
            name="Test Arrangement",
            audience=def_audience,
            location=location,
        )

        manifest = WebookPlanManifest.objects.create(
            start_date=date(2021, 1, 1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            pattern_strategy="daily__every_x_day",
            interval=1,
            recurrence_strategy="StopWithin",
            stop_within=date(2021, 1, 10),
        )

        event_serie = EventSerie.objects.create(
            arrangement=arrangement,
            serie_plan_manifest=manifest,
        )

        event_serie.events.create(
            arrangement=arrangement,
            title="Test Event",
            start=datetime(2021, 1, 1, 10, 0),
            end=datetime(2021, 1, 1, 11, 0),
        )

        rr = rem.map_serie_to_graph_event(manifest)

        self.assertEqual(rr.recurrence.pattern.type, RecurrencePatternType.Daily)
        self.assertEqual(rr.recurrence.range.type, RecurrenceRangeType.EndDate)
