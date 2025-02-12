from datetime import timedelta
from django.core.management.base import BaseCommand
from webook.onlinebooking.models import OnlineBooking, OnlineBookingSettings
from webook.arrangement.models import Event, Arrangement, Person


class Command(BaseCommand):
    help = "Fix partially complete bookings, where an OnlineBooking entity has been created but not an arrangement->event"

    def handle(self, *args, **options):
        obs = [x for x in OnlineBooking.objects.all() if not x.arrangement]
        settings = OnlineBookingSettings.objects.first()

        for ob in obs:
            self.stdout.write(f" - {ob.id} ({ob.created}) is missing arrangement.")

        for ob in obs:
            add_time_with_arbitrary_unit = lambda amount, unit: timedelta(
                weeks=amount if unit == OnlineBookingSettings.Unit.WEEKS else 0,
                days=amount if unit == OnlineBookingSettings.Unit.DAYS else 0,
                hours=amount if unit == OnlineBookingSettings.Unit.HOURS else 0,
                minutes=amount if unit == OnlineBookingSettings.Unit.MINUTES else 0,
            )

            start_time = ob.created + add_time_with_arbitrary_unit(
                settings.offset, settings.offset_unit
            )
            end_time = start_time + add_time_with_arbitrary_unit(
                settings.duration_amount, settings.duration_unit
            )

            title = settings.title_format
            title = title.replace("%BookingNr%", str(ob.id))
            if ob.school:
                title = title.replace("%Skolenavn%", ob.school.name)
            title = title.replace("%Fylkenavn%", ob.county.name)
            title = title.replace("%StartTid%", start_time.strftime("%H:%M"))
            title = title.replace("%SluttTid%", end_time.strftime("%H:%M"))
            title = title.replace("%Dato%", start_time.strftime("%d.%m.%Y"))
            if ob.school and ob.school.city_segment:
                title = title.replace(
                    "%Bydel%",
                    ob.school.city_segment.name if ob.school.city_segment.name else "",
                )

            ob_meta = {
                "school": ob.school,
                "city_segment": ob.school.city_segment if ob.school else None,
                "booking_selected_audience": ob.audience_type,
            }

            arrangement = Arrangement.objects.create(
                name=title,
                audience=ob.audience_type,
                location=settings.location,
                arrangement_type=settings.arrangement_type,
                status=settings.status_type,
                responsible=(
                    settings.main_planner.person if settings.main_planner else None
                ),
                county=ob.county,
                **ob_meta,
            )

            arrangement.save()

            ob.arrangement = arrangement

            event = Event.objects.create(
                arrangement=arrangement,
                title=title,
                status=settings.status_type,
                arrangement_type=settings.arrangement_type,
                start=start_time,
                expected_visitors=ob.visitors_count,
                actual_visitors=ob.visitors_count,
                responsible=(
                    settings.main_planner.person if settings.main_planner else None
                ),
                end=end_time,
                audience=ob.audience_type,
                county=ob.county,
                **ob_meta,
            )

            event.save()
            arrangement.save()

            ob.save()
            self.stdout.write(f" - {ob.id} ({ob.created}) has been fixed.")

        self.stdout.write(
            self.style.SUCCESS("All partially complete bookings have been fixed.")
        )
