import json
import math
import threading
import time
import unicodedata
from pathlib import Path
from statistics import mean
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import Flask, jsonify, render_template, request


BASE_DIR = Path(__file__).resolve().parent
with (BASE_DIR / "data" / "catalog.json").open(encoding="utf-8") as catalog_file:
    CATALOG = json.load(catalog_file)

app = Flask(__name__)
OVERPASS_ENDPOINTS = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
)
STORE_CACHE_TTL_SECONDS = 600
STORE_CACHE = {}
STORE_CACHE_LOCK = threading.Lock()


def normalize(value):
    normalized = unicodedata.normalize("NFKD", value.casefold())
    return "".join(character for character in normalized if not unicodedata.combining(character))


def distance_in_km(first_lat, first_lng, second_lat, second_lng):
    earth_radius_km = 6371
    lat_delta = math.radians(second_lat - first_lat)
    lng_delta = math.radians(second_lng - first_lng)
    haversine = (
        math.sin(lat_delta / 2) ** 2
        + math.cos(math.radians(first_lat))
        * math.cos(math.radians(second_lat))
        * math.sin(lng_delta / 2) ** 2
    )
    return earth_radius_km * 2 * math.atan2(math.sqrt(haversine), math.sqrt(1 - haversine))


def edit_distance(first, second, limit):
    if abs(len(first) - len(second)) > limit:
        return limit + 1

    previous_row = list(range(len(second) + 1))
    for row_index, first_character in enumerate(first, start=1):
        current_row = [row_index]
        for column_index, second_character in enumerate(second, start=1):
            current_row.append(
                min(
                    current_row[column_index - 1] + 1,
                    previous_row[column_index] + 1,
                    previous_row[column_index - 1] + (first_character != second_character),
                )
            )
        if min(current_row) > limit:
            return limit + 1
        previous_row = current_row
    return previous_row[-1]


def product_matches(product, query):
    if not query:
        return True

    searchable_words = normalize(
        " ".join([product["name"], product["category"], *product["aliases"]])
    ).split()
    for query_word in query.split():
        allowed_edits = 1 if len(query_word) < 6 else 2
        if not any(
            query_word in word or edit_distance(query_word, word, allowed_edits) <= allowed_edits
            for word in searchable_words
        ):
            return False
    return True


def fetch_nearby_stores(latitude, longitude, radius_km=3):
    radius_meters = int(max(500, min(radius_km * 1000, 5000)))
    cache_key = (round(latitude, 3), round(longitude, 3), radius_meters)
    now = time.monotonic()
    with STORE_CACHE_LOCK:
        cached = STORE_CACHE.get(cache_key)
        if cached and now - cached[0] < STORE_CACHE_TTL_SECONDS:
            return list(cached[1])

    query = (
        "[out:json][timeout:8];"
        'nwr["shop"~"^(convenience|supermarket|kiosk|greengrocer|bakery|general|variety_store)$"]'
        f"(around:{radius_meters},{latitude},{longitude});out center;"
    )
    encoded_query = urlencode({"data": query}).encode("utf-8")
    last_error = None

    for endpoint in OVERPASS_ENDPOINTS:
        request = Request(
            endpoint,
            data=encoded_query,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "BebelinPriceFinder/1.0 (OpenStreetMap nearby shops)",
            },
        )
        try:
            with urlopen(request, timeout=8) as response:
                elements = json.load(response).get("elements", [])
        except Exception as error:
            last_error = error
            continue

        stores = []
        for element in elements:
            tags = element.get("tags", {})
            center = element.get("center", {})
            store_latitude = element.get("lat", center.get("lat"))
            store_longitude = element.get("lon", center.get("lon"))
            if store_latitude is None or store_longitude is None:
                continue

            store_latitude = float(store_latitude)
            store_longitude = float(store_longitude)
            stores.append(
                {
                    "id": f"osm:{element.get('type', 'node')}:{element.get('id', '')}",
                    "name": tags.get("name") or tags.get("brand") or "Comercio sin nombre",
                    "neighborhood": (
                        tags.get("addr:suburb")
                        or tags.get("addr:neighbourhood")
                        or tags.get("addr:city")
                        or "Cerca de ti"
                    ),
                    "lat": store_latitude,
                    "lng": store_longitude,
                    "shop_type": tags.get("shop", "store"),
                    "distance_km": distance_in_km(
                        latitude, longitude, store_latitude, store_longitude
                    ),
                }
            )

        stores.sort(key=lambda store: store["distance_km"])
        stores = stores[:25]
        with STORE_CACHE_LOCK:
            STORE_CACHE[cache_key] = (now, stores)
        return list(stores)

    raise RuntimeError("No se pudo consultar OpenStreetMap") from last_error


@app.get("/")
def index():
    return render_template("index.html", catalog=CATALOG)


@app.get("/api/search")
def search():
    query = normalize(request.args.get("q", "").strip())
    category = request.args.get("category", "")
    sort_by = request.args.get("sort", "price")

    try:
        latitude = float(request.args["lat"]) if "lat" in request.args else None
        longitude = float(request.args["lng"]) if "lng" in request.args else None
    except ValueError:
        return jsonify({"error": "La ubicación debe contener coordenadas válidas."}), 400

    if (latitude is None) != (longitude is None):
        return jsonify({"error": "Se necesitan latitud y longitud."}), 400
    if latitude is not None and (
        not math.isfinite(latitude)
        or not math.isfinite(longitude)
        or not -90 <= latitude <= 90
        or not -180 <= longitude <= 180
    ):
        return jsonify({"error": "Las coordenadas están fuera de rango."}), 400

    products = {
        product["id"]: product
        for product in CATALOG["products"]
        if (not category or product["category"] == category)
        and product_matches(product, query)
    }

    data_notice = CATALOG["data_notice"]
    store_source = "demo"
    if latitude is None:
        stores = CATALOG["stores"]
    else:
        try:
            stores = fetch_nearby_stores(latitude, longitude)
            store_source = "openstreetmap"
            data_notice = (
                "Tiendas y ubicaciones de OpenStreetMap; precios estimados con el promedio "
                "de referencia. Confirma el precio en el local."
            )
        except RuntimeError:
            stores = [
                {
                    **store,
                    "distance_km": distance_in_km(
                        latitude, longitude, store["lat"], store["lng"]
                    ),
                }
                for store in CATALOG["stores"]
                if distance_in_km(latitude, longitude, store["lat"], store["lng"]) <= 5
            ]
            data_notice = (
                "No se pudo actualizar OpenStreetMap. Solo se muestran tiendas de ejemplo "
                "cercanas; sus precios no están verificados."
            )

    results = []
    for store in stores:
        for product in products.values():
            product_offers = [
                offer
                for catalog_store in CATALOG["stores"]
                for offer in catalog_store["offers"]
                if offer["product_id"] == product["id"]
            ]
            if not product_offers:
                continue

            if store_source == "openstreetmap":
                price = int(mean(offer["price"] for offer in product_offers) + 0.5)
                unit = product_offers[0]["unit"]
            else:
                offer = next(
                    (
                        item
                        for item in store["offers"]
                        if item["product_id"] == product["id"]
                    ),
                    None,
                )
                if offer is None:
                    continue
                price = offer["price"]
                unit = offer["unit"]

            results.append(
                {
                    "store_id": store["id"],
                    "store_name": store["name"],
                    "neighborhood": store["neighborhood"],
                    "lat": store["lat"],
                    "lng": store["lng"],
                    "store_source": store_source,
                    "product_id": product["id"],
                    "product_name": product["name"],
                    "detail": product["detail"],
                    "unit": unit,
                    "price": price,
                    "source": "estimated" if store_source == "openstreetmap" else offer["source"],
                    "distance_km": store.get("distance_km"),
                }
            )

    if sort_by == "distance" and latitude is not None:
        results.sort(key=lambda result: (result["distance_km"], result["price"]))
    else:
        results.sort(key=lambda result: (result["price"], result["store_name"]))

    return jsonify(
        {
            "results": results,
            "count": len(results),
            "store_count": len(stores),
            "store_source": store_source,
            "currency": CATALOG["currency"],
            "location": CATALOG["location"],
            "data_notice": data_notice,
        }
    )


@app.get("/api/categories")
def categories():
    return jsonify(CATALOG["categories"])


if __name__ == "__main__":
    app.run(debug=True)