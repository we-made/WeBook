from django.test import TestCase
from webook.arrangement.models import (
    Arrangement,
    Audience,
    Event,
    Location,
    Person,
    PlanManifest as WebookPlanManifest,
)
import webook.graph_integration.routines.mapping.repeating_event_mapping as rem
from msgraph.generated.models.day_of_week import DayOfWeek
from typing import List
from datetime import datetime, timedelta
from webook.graph_integration.models import GraphCalendar, SyncedEvent
from pytz import timezone
import webook.graph_integration.routines.calendar_sync as cal_sync


class CalendarSyncTestCase(TestCase):
    def __initialize_db(self):
        def_audience = Audience.objects.create(name="Default Audience")
        location = Location.objects.create(name="Default Location")
        arrangement = Arrangement.objects.create(
            name="Test Arrangement",
            audience=def_audience,
            location=location,
        )

        person_a: Person = Person.objects.create(
            first_name="Person",
            last_name="A",
            social_provider_id="mock_social_provider_id",
            calendar_sync_enabled=True,
        )

        person_b = Person.objects.create(
            first_name="Person",
            last_name="B",
            social_provider_id="mock_social_provider_id",
            calendar_sync_enabled=True,
        )

        person_c = Person.objects.create(
            first_name="Person",
            last_name="C",
            social_provider_id="mock_social_provider_id",
            calendar_sync_enabled=True,
        )

        dtz = timezone("Europe/Oslo")

        event_a = Event.objects.create(
            arrangement=arrangement,
            title="Event A",
            start=datetime.now(tz=dtz) + timedelta(days=1),
            end=datetime.now(tz=dtz) + timedelta(days=2),
        )
        event_a.people.add(person_a)
        event_a.save()

        event_b = Event.objects.create(
            arrangement=arrangement,
            title="Event B",
            start=datetime.now(tz=dtz) + timedelta(days=1),
            end=datetime.now(tz=dtz) + timedelta(days=2),
        )
        event_b.people.add(person_a, person_b)

        event_c = Event.objects.create(
            arrangement=arrangement,
            title="Event C",
            start=datetime.now(tz=dtz) + timedelta(days=1),
            end=datetime.now(tz=dtz) + timedelta(days=2),
        )
        synced_event_c = SyncedEvent.objects.create(
            webook_event=event_c,
            graph_calendar=GraphCalendar.objects.create(
                name="Test Calendar", calendar_id="test_calendar_id", person=person_a
            ),
            event_hash=event_c.hash_key(),
        )

        event_b.save()

        historic_event = Event.objects.create(
            arrangement=arrangement,
            title="Historic Event",
            start=datetime.now(tz=dtz) - timedelta(days=2),
            end=datetime.now(tz=dtz) - timedelta(days=1),
        )
        historic_event.people.add(person_c)

        return {
            "person_a": person_a,
            "person_b": person_b,
            "person_c": person_c,
            "event_a": event_a,
            "event_b": event_b,
            "event_c": event_c,
            "historic_event": historic_event,
        }

    def test_instruction_calculation(self):
        """Assert that the instruction calculation returns the correct number of instructions."""
        d = self.__initialize_db()
        instructions = cal_sync._calculate_instructions(
            [d["event_a"], d["event_b"]], [d["person_a"]]
        )

        self.assertEqual(len(instructions), 2)

    def test_instruction_calculation_ignores_event_in_sync(self):
        """Assert that the instruction calculation ignores events that are already in sync."""
        d = self.__initialize_db()
        instructions = cal_sync._calculate_instructions([d["event_c"]], [d["person_a"]])
        self.assertEqual(len(instructions), 0)

    def test_instruction_wants_to_update_out_of_sync_event(self):
        """Assert that the instruction calculation wants to update an event that is out of sync."""
        d = self.__initialize_db()
        d["event_c"].title = "Updated Title"
        d["event_c"].save()

        instructions = cal_sync._calculate_instructions([d["event_c"]], [d["person_a"]])
        self.assertEqual(len(instructions), 1)
        self.assertEqual(instructions[0][2], cal_sync.Operation.UPDATE)

    def test_instruction_calculation_handles_no_events_raises_value_error(self):
        """Assert that the instruction calculation returns an empty list when no events are supplied."""
        with self.assertRaises(ValueError):
            cal_sync._calculate_instructions([], [])

    def test_instruction_calculation_without_persons(self):
        """Assert that the instruction calculation returns the correct number of instructions."""
        d = self.__initialize_db()
        instructions = cal_sync._calculate_instructions(
            [d["event_a"], d["event_b"]], []
        )

        # Since no persons supplied = all persons
        self.assertEqual(len(instructions), 3)

    def test_instruction_calculation_does_not_cross(self):
        """In the case that multiple persons are supplied to the calculation,
        assert that a person is not added to an event that they are not a part of.
        """

        d = self.__initialize_db()
        instructions = cal_sync._calculate_instructions(
            [d["event_a"], d["event_b"]], [d["person_a"], d["person_b"]]
        )

        self.assertEqual(len(instructions), 3)

    def test_get_events_for_selection(self):
        d = self.__initialize_db()

        events = cal_sync._get_events_matching_criteria(
            future_only=True,
            persons=[d["person_a"]],
            event_ids=[d["event_a"].id, d["event_b"].id],
        )

        self.assertEqual(len(events), 2)

    def test_get_events_for_selection_ignores_specified_event_if_not_in_criteria(self):
        d = self.__initialize_db()

        # event_a is not associated with person_b so it should not be returned
        events = cal_sync._get_events_matching_criteria(
            future_only=True,
            persons=[d["person_b"]],
            event_ids=[d["event_a"].id],
        )

        self.assertEqual(len(events), 0)

    def test_get_events_matching_criteria_respects_only_future_argument(self):
        d = self.__initialize_db()

        only_future_events = cal_sync._get_events_matching_criteria(
            future_only=True, persons=[d["person_c"]], event_ids=[]
        )

        all_events = cal_sync._get_events_matching_criteria(
            future_only=False, persons=[d["person_c"]], event_ids=[]
        )

        self.assertEqual(len(only_future_events), 0)
        self.assertEqual(len(all_events), 1)

    def test_convert_event_to_graph_event(self):
        pass
