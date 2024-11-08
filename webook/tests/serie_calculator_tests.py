import pytest
from webook.arrangement.models import PlanManifest
import webook.utils.serie_calculator as sc
from datetime import time, date, datetime
from pytz import timezone


def test_generate_every_weekday():
    """Test the pattern strategy every weekday"""
    manifest = PlanManifest(
        pattern="daily",
        title="Unit Test",
        pattern_strategy="daily__every_weekday",
        recurrence_strategy="StopWithin",
        start_time=time(9, 0),
        end_time=time(14, 0),
        start_date=date(2024, 11, 3),
        stop_within=date(2024, 11, 9),
    )

    results: list = sc.calculate_serie(serie_manifest=manifest)
    assert len(results) == 5
    tz = timezone("Europe/Oslo")

    # Monday is 04.11.2024. But our range starts on sunday 03.11.2024
    # Let's ensure we don't have any results for Sunday
    assert results[0].start == tz.localize(datetime(2024, 11, 4, 9, 0))
    assert results[0].end == tz.localize(datetime(2024, 11, 4, 14, 0))

    # Friday is 08.11.2024 - but our range goes to 09.11.2024 (Saturday)
    # Let's ensure we don't have any results for Saturday
    assert results[-1].start == tz.localize(datetime(2024, 11, 8, 9, 0))
    assert results[-1].end == tz.localize(datetime(2024, 11, 8, 14, 0))

    assert results[0].title == "Unit Test"


def test_weekly_standard_pattern():
    """Test the pattern strategy weekly"""
    manifest = PlanManifest(
        pattern="weekly",
        title="Unit Test",
        pattern_strategy="weekly__standard",
        recurrence_strategy="StopWithin",
        start_time=time(9, 0),
        end_time=time(14, 0),
        start_date=date(2024, 11, 1),
        stop_within=date(2024, 11, 30),
        interval=2,  # Every X weeks
        monday=True,
        wednesday=True,
    )

    results: list = sc.calculate_serie(serie_manifest=manifest)
    print(results)
    assert len(results) == 4

    # The 01.11 is a sunday. Since we have selected every other week, the next week (week 2 of month) will be skipped
    # So that's why we start on 11.11
    # One could debate if one should actually just not skip until we've hit a week where we've been able to apply the pattern.
    # I'm not sure - but this behaviour has been in live for a while now, so changing it might not be the best idea.
    # That being said - it isn't a bug per se. More of a question of what is the best and most reasonable behaviour.
    assert results[0].start == timezone("Europe/Oslo").localize(
        datetime(2024, 11, 11, 9, 0)
    )

    assert all([x.start.weekday() in [0, 2] for x in results])


def test_month_every_x_day_every_y_month():
    """Test the pattern strategy monthly every X day every Y month"""
    manifest = PlanManifest(
        pattern="monthly",
        title="Unit Test",
        pattern_strategy="month__every_x_day_every_y_month",
        recurrence_strategy="StopWithin",
        start_time=time(9, 0),
        end_time=time(14, 0),
        start_date=date(2024, 10, 1),
        stop_within=date(2024, 12, 31),
        interval=1,
        day_of_month=15,
    )

    results: list = sc.calculate_serie(serie_manifest=manifest)

    assert len(results) == 3


def test_month_every_arbitrary_date_of_month():
    """Test the pattern strategy monthly every arbitrary date of month"""

    def create_manifest(arbitrator: int):
        return PlanManifest(
            pattern="monthly",
            title="Unit Test",
            pattern_strategy="month__every_arbitrary_date_of_month",
            recurrence_strategy="StopWithin",
            start_time=time(9, 0),
            end_time=time(14, 0),
            start_date=date(2024, 10, 2),
            stop_within=date(2024, 12, 31),
            interval=1,
            arbitrator=arbitrator,
        )

    results_every_last: list = sc.calculate_serie(serie_manifest=create_manifest(4))
    assert len(results_every_last) == 3

    results_every_fourth: list = sc.calculate_serie(serie_manifest=create_manifest(3))
    assert len(results_every_fourth) == 3

    results_every_third: list = sc.calculate_serie(serie_manifest=create_manifest(2))
    assert len(results_every_third) == 3

    results_every_second: list = sc.calculate_serie(serie_manifest=create_manifest(1))
    assert len(results_every_second) == 3

    results_every_first: list = sc.calculate_serie(serie_manifest=create_manifest(0))
    assert len(results_every_first) == 3


def test_yearly_every_x_of_month():
    """Test a yearly pattern every X of month"""
    manifest = PlanManifest(
        pattern="yearly",
        title="Unit Test",
        pattern_strategy="yearly__every_x_of_month",
        recurrence_strategy="StopWithin",
        start_time=time(9, 0),
        end_time=time(14, 0),
        start_date=date(2020, 1, 1),
        stop_within=date(2024, 12, 31),
        month=1,
        day_of_month=1,
    )

    results: list = sc.calculate_serie(serie_manifest=manifest)

    assert len(results) == 5


def test_yearly_every_x_of_month_with_interval():
    """Test a yearly pattern every X of month with interval"""
    manifest = PlanManifest(
        pattern="yearly",
        title="Unit Test",
        pattern_strategy="yearly__every_x_of_month",
        recurrence_strategy="StopWithin",
        start_time=time(9, 0),
        end_time=time(14, 0),
        start_date=date(2020, 1, 1),
        stop_within=date(2024, 12, 31),
        month=1,
        day_of_month=1,
        interval=2,
    )

    results: list = sc.calculate_serie(serie_manifest=manifest)

    assert len(results) == 2


def test_yearly_every_arbitrary_weekday_in_month():
    """Test a yearly pattern every arbitrary weekday in month"""
    manifest = PlanManifest(
        pattern="yearly",
        title="Unit Test",
        pattern_strategy="yearly__every_arbitrary_weekday_in_month",
        recurrence_strategy="StopWithin",
        start_time=time(9, 0),
        end_time=time(14, 0),
        start_date=date(2020, 1, 1),
        stop_within=date(2024, 12, 31),
        arbitrator=3,
        day_of_week=1,
        month=1,
    )  # Yearly, every first day of the third week in January, starting from 2020

    results: list = sc.calculate_serie(serie_manifest=manifest)

    assert len(results) == 5


def test_recurrence_stop_after_x_instances():
    manifest = PlanManifest(
        pattern="daily",
        title="Unit Test",
        pattern_strategy="daily__every_weekday",
        recurrence_strategy="StopAfterXInstances",
        start_time=time(9, 0),
        end_time=time(14, 0),
        start_date=date(2024, 11, 3),
        stop_after_x_occurences=3,
    )

    results: list = sc.calculate_serie(serie_manifest=manifest)

    assert len(results) == 3


def test_recurrence_forever():
    manifest = PlanManifest(
        pattern="daily",
        title="Unit Test",
        pattern_strategy="daily__every_weekday",
        recurrence_strategy="NoStopDate",
        start_time=time(9, 0),
        end_time=time(14, 0),
        start_date=date(2024, 11, 3),
        project_x_months_into_future=1,
    )

    results: list = sc.calculate_serie(serie_manifest=manifest)

    assert len(results) == 20


def test_generate_every_x_day():
    """Test the pattern strategy every X day"""
    manifest = PlanManifest(
        pattern="daily",
        title="Unit Test",
        pattern_strategy="daily__every_x_day",
        recurrence_strategy="StopWithin",
        start_time=time(9, 0),
        end_time=time(14, 0),
        start_date=date(2024, 11, 3),
        stop_within=date(2024, 11, 9),
        interval=2,
        day_of_week=1,
    )

    results: list = sc.calculate_serie(serie_manifest=manifest)

    assert len(results) == 4  # 03, 05, 07, 09
    tz = timezone("Europe/Oslo")
    assert results[0].start == tz.localize(datetime(2024, 11, 3, 9, 0))
    assert results[1].start == tz.localize(datetime(2024, 11, 5, 9, 0))
    assert results[2].start == tz.localize(datetime(2024, 11, 7, 9, 0))
    assert results[3].start == tz.localize(datetime(2024, 11, 9, 9, 0))


def test_generate_with_non_standard_tz():
    manifest = PlanManifest(
        pattern="daily",
        title="Unit Test",
        pattern_strategy="daily__every_weekday",
        recurrence_strategy="StopWithin",
        start_time=time(9, 0),
        end_time=time(14, 0),
        start_date=date(2024, 11, 3),
        stop_within=date(2024, 11, 9),
    )

    tz = timezone("America/New_York")

    results: list = sc.calculate_serie(serie_manifest=manifest, tz=tz)
    assert results[0].start.tzinfo.zone == "America/New_York"
