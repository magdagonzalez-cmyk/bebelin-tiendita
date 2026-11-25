import json
import math
import unicodedata
from pathlib import Path

from flask import Flask, jsonify, render_template, request


BASE_DIR = Path(__file__).resolve().parent
with (BASE_DIR / "data" / "catalog.json").open(encoding="utf-8") as catalog_file:
    CATALOG = json.load(catalog_file)

app = Flask(__name__)


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

    products = {
        product["id"]: product
        for product in CATALOG["products"]
        if (not category or product["category"] == category)
        and (
            not query
            or query in normalize(
                " ".join([product["name"], product["category"], *product["aliases"]])
            )
        )
    }

    results = []
    for store in CATALOG["stores"]:
        for offer in store["offers"]:
            product = products.get(offer["product_id"])
            if product is None:
                continue

            distance = None
            if latitude is not None:
                distance = distance_in_km(latitude, longitude, store["lat"], store["lng"])

            results.append(
                {
                    "store_id": store["id"],
                    "store_name": store["name"],
                    "neighborhood": store["neighborhood"],
                    "lat": store["lat"],
                    "lng": store["lng"],
                    "product_id": product["id"],
                    "product_name": product["name"],
                    "detail": product["detail"],
                    "unit": offer["unit"],
                    "price": offer["price"],
                    "source": offer["source"],
                    "distance_km": distance,
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
            "currency": CATALOG["currency"],
            "location": CATALOG["location"],
            "data_notice": CATALOG["data_notice"],
        }
    )


@app.get("/api/categories")
def categories():
    return jsonify(CATALOG["categories"])


if __name__ == "__main__":
    app.run(debug=True)