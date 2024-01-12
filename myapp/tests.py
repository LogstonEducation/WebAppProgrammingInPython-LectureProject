from django.test import TestCase

from myapp import utils


class UtilsTests(TestCase):
    def test_get_lat_lon_from_web(self):
        lat, lon, url = utils.get_lat_lon('San Francisco')
        self.assertAlmostEqual(lat, 37.77750, places=5)
        self.assertAlmostEqual(lon, -122.41639, places=5)
        self.assertEqual(url, 'https://en.wikipedia.org/wiki/San_Francisco')

    def test_get_lat_lon_dicts(self):
        details_by_lat_lon = utils.get_lat_lon_dicts(['San Francisco', 'New York City'])
        self.assertEqual(
            details_by_lat_lon,
            {
                (37.7775, -122.41639): ('https://en.wikipedia.org/wiki/San_Francisco', 'San Francisco'),
                (40.71278, -74.00611): ('https://en.wikipedia.org/wiki/New_York_City', 'New York City'),
            }
        )