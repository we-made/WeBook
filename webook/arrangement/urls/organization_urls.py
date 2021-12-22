from django.urls import path
from webook.arrangement.views import (
    organization_list_view,
    organization_create_view,
    organization_update_view,
    organization_detail_view,
    organization_delete_view,
    organization_person_member_list_view
)


organization_urls = [
    path(
        route="organization/list/",
        view=organization_list_view,
        name="organization_list",
    ),
    path(
        route="organization/create/",
        view=organization_create_view,
        name="organization_create",
    ),
    path(
        route="organization/edit/<slug:slug>",
        view=organization_update_view,
        name="organization_edit",
    ),
    path(
        route="organization/<slug:slug>/",
        view=organization_detail_view,
        name="organization_detail",
    ),
    path(
        route="organization/delete/<slug:slug>/",
        view=organization_delete_view,
        name="organization_delete"
    ),

    path(
        route="person/organizationmemberlist?organization=<str:organization>",
        view=organization_person_member_list_view,
        name="organizationmemberlist"
    ),
]