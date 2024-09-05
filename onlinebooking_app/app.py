# save this as app.py
from flask import Flask, url_for, render_template, request
from api_client import WeBookApiClient
import httpx
import config
from flask_cors import CORS

app = Flask(__name__)
api_client = WeBookApiClient()

CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/")
def index():
    return render_template("index.html", app_title=config.APP_TITLE) + render_template(
        "table_component.html"
    )


@app.route("/counties")
def counties():
    response: httpx.Response = api_client.get("/onlinebooking/county/list")
    return response.json()


@app.route("/schools/<county_id>")
def schools(county_id: int):
    limit = request.args.get("limit", 10)
    page = request.args.get("page", 0)
    search = request.args.get("search", "")
    sort_by = request.args.get("sort_by", "name")
    audience_id = request.args.get("audience_id", None)

    if audience_id is None:
        raise ValueError("audience_id is required")

    response: httpx.Response = api_client.get(
        f"/onlinebooking/school/list",
        params={
            "county_id": county_id,
            "limit": limit,
            "page": page,
            "fields_to_search": "name" if search else "",
            "search": search if search else "",
            "sort_by": sort_by,
            "sort_order": "desc",
            "audience_id": audience_id,
        },
    )
    return response.json()


@app.route("/schools_v1/<county_id>")
def schools(county_id: int):
    limit = request.args.get("limit", 10)
    page = request.args.get("page", 0)
    search = request.args.get("search", "")
    sort_by = request.args.get("sort_by", "name")

    response: httpx.Response = api_client.get(
        f"/onlinebooking/school/list",
        params={
            "county_id": county_id,
            "limit": limit,
            "page": page,
            "fields_to_search": "name" if search else "",
            "search": search if search else "",
            "sort_by": sort_by,
            "sort_order": "desc",
        },
    )
    return response.json()


@app.route("/city_segments/<county_id>")
def city_segments(county_id: int):
    response: httpx.Response = api_client.get(
        "/onlinebooking/city_segment/list?county_id=" + str(county_id)
    )
    return response.json()


@app.route("/audiences")
def audiences():
    response: httpx.Response = api_client.get("/arrangement/audience/list")
    return response.json()


@app.post("/online_booking")
def online_booking():
    data = request.json
    if "school_id" not in data:
        data["school_id"] = None

    response: httpx.Response = api_client.post(
        "/onlinebooking/online_booking/create", json=data
    )
    return response.json()


@app.get("/online_booking_settings")
def online_booking_settings():
    response: httpx.Response = api_client.get("/onlinebooking/online_booking/settings")
    return response.json()
