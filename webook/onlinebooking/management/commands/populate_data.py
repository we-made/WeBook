from django.core.management.base import BaseCommand
from requests import get
from webook.arrangement.models import Audience
from webook.onlinebooking.models import School, County

# NSR = Nasjonalt Skoleregister (National School Register)
# Registry containing information about all schools in Norway
# https://data-nsr.udir.no/swagger/index.html
NSR_API_URL = "https://data-nsr.udir.no/v4/"

# Kartverket - Administrative enheter (Administrative units)
# Registry containing information about all municipalities in Norway
GEO_AU_API_URL = "https://ws.geonorge.no/kommuneinfo/v1/"


class Command(BaseCommand):
    help = "Populate the database with municipalities and schools"

    def __get_counties(self):
        response = get(f"{GEO_AU_API_URL}fylker")
        response.raise_for_status()
        return response.json()

    def __get_schools(self):
        schools = []
        page_num = 1
        while True:
            response = get(
                f"{NSR_API_URL}enheter",
                params={"sidenummer": page_num, "antallperside": 1000},
            )
            response.raise_for_status()
            data = response.json()
            schools += data["EnhetListe"]

            print(response, len(data["EnhetListe"]), page_num)

            if len(data["EnhetListe"]) < 1000:
                break

            page_num += 1

        return [
            x
            for x in schools
            if x["ErAktiv"] and x["ErSkole"] and x["ErOffentligSkole"]
        ]

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

        our_schools = School.objects.all()
        schools_in_nsr = self.__get_schools()

        print(len(schools_in_nsr))

        for school in schools_in_nsr:
            self.stdout.write(f"School: {school['Navn']}")

            if not our_schools.filter(name=school["Navn"]).exists():
                print(school["Fylkesnummer"])
                try:
                    county = County.objects.get(county_number=school["Fylkesnummer"])
                except County.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"County with number {school['Fylkesnummer']} not found"
                        )
                    )
                    continue

                audience = None

                if "voksenopplæring" in school["Navn"].lower():
                    audience = Audience.objects.get(name="Voksenopplæring")
                elif school["ErGrunnskole"]:
                    if (
                        "ungdomsskole" in school["Navn"].lower()
                        or "ungdomsskule" in school["Navn"].lower()
                    ):
                        audience = Audience.objects.get(name="Ungdomskole")
                    else:
                        audience = Audience.objects.get(name="Mellomtrinn")
                elif school["ErVideregaaendeSkole"]:
                    audience = Audience.objects.get(name="Videregående")

                School.objects.create(
                    name=school["Navn"], county=county, audience=audience
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Created school {school['Navn']}")
                )
