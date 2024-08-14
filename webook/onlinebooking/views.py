from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, CreateView, UpdateView

from webook.onlinebooking.models import CitySegment, County, OnlineBooking, School


class DashboardView(View):
    def get(self, request):
        return render(request, "dashboard.html")


class OnlineBookingDetailView(DetailView):
    model = OnlineBooking
    template_name = "booking_detail.html"
    context_object_name = "booking"


class CountyDetailView(DetailView):
    model = County
    template_name = "county_detail.html"
    context_object_name = "county"


class SchoolDetailView(DetailView):
    model = School
    template_name = "school_detail.html"
    context_object_name = "school"


class CitySegmentDetailView(DetailView):
    model = CitySegment
    template_name = "city_segment_detail.html"
    context_object_name = "city_segment"
