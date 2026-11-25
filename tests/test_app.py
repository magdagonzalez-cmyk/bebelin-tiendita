import io
import json
import unittest
from unittest.mock import patch

from app import STORE_CACHE, app, fetch_nearby_stores


class SearchApiTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_homepage_renders_search_and_map(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"TIENDAS EN EL MAPA", response.data)
        self.assertIn("Precios de referencia".encode(), response.data)

    def test_search_matches_alias_and_sorts_by_price(self):
        response = self.client.get("/api/search?q=pan")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["count"], 4)
        self.assertEqual(data["results"][0]["price"], 1750)
        self.assertTrue(all(result["source"] == "estimated" for result in data["results"]))

    def test_search_normalizes_accents_and_filters_category(self):
        response = self.client.get("/api/search?q=galleta&category=Galletas%20y%20snacks")
        data = response.get_json()

        self.assertEqual(data["count"], 4)
        self.assertTrue(all(result["product_id"] == "cookies" for result in data["results"]))

    def test_distance_sort_needs_and_uses_coordinates(self):
        nearby_store = {
            "id": "osm:node:1",
            "name": "Almacén cercano",
            "neighborhood": "Providencia",
            "lat": -33.4264,
            "lng": -70.6166,
            "distance_km": 0,
            "shop_type": "convenience",
        }
        with patch("app.fetch_nearby_stores", return_value=[nearby_store]):
            response = self.client.get(
                "/api/search?q=leche&sort=distance&lat=-33.4264&lng=-70.6166"
            )
        data = response.get_json()

        self.assertEqual(data["results"][0]["neighborhood"], "Providencia")
        self.assertEqual(data["results"][0]["distance_km"], 0)
        self.assertEqual(data["store_source"], "openstreetmap")
        self.assertEqual(data["results"][0]["store_name"], "Almacén cercano")
        self.assertEqual(data["store_count"], 1)
        self.assertEqual(data["results"][0]["price"], 1270)

    def test_search_rejects_incomplete_location(self):
        response = self.client.get("/api/search?q=pan&lat=-33.4")

        self.assertEqual(response.status_code, 400)

    def test_search_rejects_out_of_range_location(self):
        response = self.client.get("/api/search?q=pan&lat=91&lng=-70")

        self.assertEqual(response.status_code, 400)

    def test_location_search_falls_back_when_openstreetmap_is_unavailable(self):
        with patch("app.fetch_nearby_stores", side_effect=RuntimeError("offline")):
            response = self.client.get("/api/search?q=pan&lat=-34&lng=-71")
        data = response.get_json()

        self.assertEqual(data["results"], [])
        self.assertEqual(data["store_source"], "demo")
        self.assertIn("OpenStreetMap", data["data_notice"])

    def test_openstreetmap_results_are_parsed_sorted_and_cached(self):
        STORE_CACHE.clear()
        payload = {
            "elements": [
                {
                    "type": "node",
                    "id": 12,
                    "lat": -33.45,
                    "lon": -70.67,
                    "tags": {"name": "Almacén cercano", "shop": "convenience", "addr:suburb": "Centro"},
                },
                {
                    "type": "way",
                    "id": 34,
                    "center": {"lat": -33.46, "lon": -70.68},
                    "tags": {"brand": "Mercado", "shop": "supermarket"},
                },
            ]
        }
        response = io.BytesIO(json.dumps(payload).encode("utf-8"))

        with patch("app.urlopen", return_value=response) as mocked_urlopen:
            stores = fetch_nearby_stores(-33.4489, -70.6693)
            cached_stores = fetch_nearby_stores(-33.4489, -70.6693)

        self.assertEqual(stores[0]["name"], "Almacén cercano")
        self.assertEqual(stores[0]["neighborhood"], "Centro")
        self.assertLess(stores[0]["distance_km"], stores[1]["distance_km"])
        self.assertEqual(cached_stores, stores)
        mocked_urlopen.assert_called_once()

    def test_search_finds_new_daily_products(self):
        response = self.client.get("/api/search?q=detergente")
        data = response.get_json()

        self.assertEqual(data["count"], 4)
        self.assertTrue(all(result["product_id"] == "detergent" for result in data["results"]))

    def test_categories_include_personal_care_and_cleaning(self):
        response = self.client.get("/api/categories")

        self.assertIn("Cuidado personal", response.get_json())
        self.assertIn("Limpieza del hogar", response.get_json())

    def test_search_accepts_one_or_two_typing_errors(self):
        one_error = self.client.get("/api/search?q=deterjente").get_json()
        two_errors = self.client.get("/api/search?q=galetaz").get_json()

        self.assertEqual(one_error["count"], 4)
        self.assertTrue(all(result["product_id"] == "detergent" for result in one_error["results"]))
        self.assertEqual(two_errors["count"], 4)
        self.assertTrue(all(result["product_id"] == "cookies" for result in two_errors["results"]))

    def test_unknown_product_returns_empty_results(self):
        response = self.client.get("/api/search?q=not-a-product")

        self.assertEqual(response.get_json()["results"], [])

if __name__ == "__main__":
    unittest.main()