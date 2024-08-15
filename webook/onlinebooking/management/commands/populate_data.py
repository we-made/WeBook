from typing import Dict, List
from django.core.management.base import BaseCommand
from requests import get
from webook.arrangement.models import Audience
from webook.onlinebooking.models import CitySegment, School, County

# Kartverket - Administrative enheter (Administrative units)
# Registry containing information about all municipalities in Norway
GEO_AU_API_URL = "https://ws.geonorge.no/kommuneinfo/v1/"


class Command(BaseCommand):
    help = "Populate the database with municipalities and schools"

    def __get_counties(self):
        response = get(f"{GEO_AU_API_URL}fylker")
        response.raise_for_status()
        return response.json()

    def handle(self, *args, **options):
        our_counties = County.objects.all()
        counties_in_geo_api = self.__get_counties()
        for county in counties_in_geo_api:
            self.stdout.write(f"County: {county['fylkesnavn']}")

            if not our_counties.filter(county_number=county["fylkesnummer"]).exists():
                County.objects.create(
                    name=county["fylkesnavn"], county_number=county["fylkesnummer"]
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Created county {county['fylkesnavn']}")
                )

        oslo_schools_data: List[Dict[str, str]] = []
        with open("oslo_schools_initialization.csv") as f:
            oslo_schools_data = [
                {"School": x[0], "CitySegment": x[1]}
                for x in [n.split(",") for n in f.readlines()]
            ]

        if not County.objects.filter(name="Oslo").exists():
            County.objects.create(name="Oslo", city_segment_enabled=True)
            self.stdout.write(self.style.SUCCESS(f"Created county Oslo"))

        for school_data in oslo_schools_data:
            segment = school_data["CitySegment"]
            if not CitySegment.objects.filter(name=segment).exists():
                CitySegment.objects.create(
                    name=segment, county=County.objects.get(name="Oslo")
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created city segment {school_data['CitySegment']}"
                    )
                )

            if not School.objects.filter(name=school_data["School"]).exists():
                School.objects.create(
                    name=school_data["School"],
                    county=County.objects.get(name="Oslo"),
                    city_segment=CitySegment.objects.get(name=segment),
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Created school {school_data['School']}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"School {school_data['School']} already exists")
                )
