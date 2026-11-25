import unittest

from app import app


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
        response = self.client.get("/api/search?q=leche&sort=distance&lat=-33.4264&lng=-70.6166")
        data = response.get_json()

        self.assertEqual(data["results"][0]["neighborhood"], "Providencia")
        self.assertEqual(data["results"][0]["distance_km"], 0)

    def test_search_rejects_incomplete_location(self):
        response = self.client.get("/api/search?q=pan&lat=-33.4")

        self.assertEqual(response.status_code, 400)

    def test_unknown_product_returns_empty_results(self):
        response = self.client.get("/api/search?q=not-a-product")

        self.assertEqual(response.get_json()["results"], [])

if __name__ == "__main__":
    unittest.main()