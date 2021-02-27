from datetime import datetime as dt
from datetime import tzinfo, timedelta, timezone
import unittest

from cdjs import serialize_date


class GMT1(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=1)
    def dst(self, dt):
        return timedelta(0)
    def tzname(self, dt):
        return "Europe/Prague"


class GMT2(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=-3)
    def dst(self, dt):
        return timedelta(0)
    def tzname(self, dt):
        return "Custom2/Custom2"


class CustomGMT(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=1, seconds=1800)
    def dst(self, dt):
        return timedelta(0)
    def tzname(self, dt):
        return "Custom/Custom"


class CustomGMT2(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=-1, seconds=-1800)
    def dst(self, dt):
        return timedelta(0)
    def tzname(self, dt):
        return "Custom22/Custom22"

# TODO: update tests for dates < 1970
class TestSerialization(unittest.TestCase):

    def test_uno(self):
        """datetime and year < 1970 without TZ info without microseconds
        """
        d = dt(1945, 5, 9, hour=18, minute=52, second=56, tzinfo=None)
        with self.assertRaises(ValueError):
            serialize_date(d)
        # self.assertEqual(
        #     serialize_date(d),
        #     {"$date": "1945-05-09T18:52:56.000Z"}
        # )

    def test_dos(self):
        """datetime and year < 1970 without TZ info without microseconds (leading zeros)
        """
        d = dt(1945, 5, 9, hour=3, minute=3, second=3, tzinfo=None)
        with self.assertRaises(ValueError):
            serialize_date(d)
        # self.assertEqual(
        #     serialize_date(d),
        #     {"$date": "1945-05-09T03:03:03.000Z"}
        # )

    def test_tres(self):
        """datetime and year < 1970 without TZ info without TZ with microseconds
        """
        d = dt(1945, 12, 29, hour=0, minute=0, second=0, microsecond=447000, tzinfo=None)
        with self.assertRaises(ValueError):
            serialize_date(d)
        # self.assertEqual(
        #     serialize_date(d),
        #     {"$date": "1945-12-29T00:00:00.447Z"}
        # )

    def test_cuatro(self):
        """datetime and year < 1970 with TZ info with TZ without microseconds
        """
        d = dt(1945, 5, 9, hour=18, minute=52, second=56, microsecond=0, tzinfo=timezone.utc)
        with self.assertRaises(ValueError):
            serialize_date(d)
        # self.assertEqual(
        #     serialize_date(d),
        #     {"$date": "1945-05-09T18:52:56.000Z"}
        # )

    def test_sinco(self):
        """datetime and year < 1970 with TZ info (non utc) with TZ without microseconds
        """
        d = dt(1945, 5, 9, hour=18, minute=52, second=56, microsecond=0, tzinfo=GMT1())
        with self.assertRaises(ValueError):
            serialize_date(d)
        # self.assertEqual(
        #     serialize_date(d),
        #     {"$date": "1945-05-09T17:52:56.000Z"}
        # )

    def test_seis(self):
        """datetime and year < 1970 with TZ info with TZ with microseconds
        """
        d = dt(1945, 5, 9, hour=18, minute=52, second=56, microsecond=678000, tzinfo=timezone.utc)
        with self.assertRaises(ValueError):
            serialize_date(d)
        # self.assertEqual(
        #     serialize_date(d),
        #     {"$date": "1945-05-09T18:52:56.678Z"}
        # )

    def test_siete(self):
        """datetime and year < 1970 with TZ info (non utc) with TZ with microseconds
        """
        d = dt(1945, 5, 9, hour=18, minute=52, second=56, microsecond=718000, tzinfo=GMT1())
        with self.assertRaises(ValueError):
            serialize_date(d)
        # self.assertEqual(
        #     serialize_date(d),
        #     {"$date": "1945-05-09T17:52:56.718Z"}
        # )

    def test_ocho(self):
        """datetime and year < 1970 with TZ info (non utc, non even ) with TZ with microseconds
        """
        d = dt(1945, 5, 9, hour=18, minute=52, second=56, microsecond=718000, tzinfo=CustomGMT())
        with self.assertRaises(ValueError):
            serialize_date(d)
        # self.assertEqual(
        #     serialize_date(d),
        #     {"$date": "1945-05-09T17:22:56.718Z"}
        # )

    def test_nueve(self):
        """default() with ISO datetime representation without TZ info without Epoch Aware without ms
        """
        d = dt(1921, 2, 18, hour=14, minute=4, second=36, microsecond=0)
        with self.assertRaises(ValueError):
            serialize_date(d)
        # self.assertEqual(
        #     serialize_date(d),
        #     {"$date": "1921-02-18T14:04:36.000Z"}
        # )

    def test_diez(self):
        """default() with ISO datetime representation without TZ info with Epoch Aware without ms
        """
        d = dt(2021, 2, 18, hour=14, minute=4, second=36, microsecond=0)
        self.assertEqual(
            serialize_date(d),
            {"$date": "2021-02-18T14:04:36Z"}
        )

    def test_once(self):
        """default() with ISO datetime representation without TZ info without Epoch Aware with ms
        """
        d = dt(1921, 2, 18, hour=14, minute=4, second=36, microsecond=47000)
        with self.assertRaises(ValueError):
            serialize_date(d)
        # self.assertEqual(
        #     serialize_date(d),
        #     {"$date": "1921-02-18T14:04:36.047Z"}
        # )

    def test_doce(self):
        """default() with ISO datetime representation without TZ info with Epoch Aware with ms
        """
        d = dt(2021, 2, 18, hour=14, minute=4, second=36, microsecond=28000)
        self.assertEqual(
            serialize_date(d),
            {"$date": "2021-02-18T14:04:36.028Z"}
        )

    def test_trece(self):
        """default() with ISO datetime representation with TZ info without Epoch Aware without ms
        """
        d = dt(1921, 2, 18, hour=14, minute=4, second=36, microsecond=0, tzinfo=GMT1())
        with self.assertRaises(ValueError):
            serialize_date(d)
        # self.assertEqual(
        #     serialize_date(d),
        #     {"$date": "1921-02-18T13:04:36.000Z"}
        # )

    def test_catorce(self):
        """default() with ISO datetime representation with TZ info without Epoch Aware with ms
        """
        d = dt(1921, 2, 18, hour=14, minute=4, second=36, microsecond=28000, tzinfo=GMT1())
        with self.assertRaises(ValueError):
            serialize_date(d)
        # self.assertEqual(
        #     serialize_date(d),
        #     {"$date": "1921-02-18T13:04:36.028Z"}
        # )

    def test_quince(self):
        """default() with ISO datetime representation with TZ info with Epoch Aware without ms
        """
        d = dt(2021, 2, 18, hour=14, minute=4, second=36, microsecond=0, tzinfo=GMT1())
        self.assertEqual(
            serialize_date(d),
            {"$date": "2021-02-18T14:04:36+0100"}
        )

    def test_dieciseis(self):
        """default() with ISO datetime representation with TZ info with Epoch Aware with ms
        """
        d = dt(2021, 2, 18, hour=14, minute=4, second=36, microsecond=36000, tzinfo=GMT1())
        self.assertEqual(
            serialize_date(d),
            {"$date": "2021-02-18T14:04:36.036+0100"}
        )

    def test_diecisiete(self):
        """default() with ISO datetime representation with TZ info with Epoch Aware without ms at the day edge
        """
        d = dt(2021, 2, 18, hour=0, minute=4, second=36, microsecond=0, tzinfo=GMT1())
        self.assertEqual(
            serialize_date(d),
            {"$date": "2021-02-18T00:04:36+0100"}
        )

    def test_dieciocho(self):
        """default() with ISO datetime representation with TZ info with Epoch Aware with ms at the day edge
        """
        d = dt(2021, 2, 18, hour=0, minute=4, second=36, microsecond=36000, tzinfo=GMT1())
        self.assertEqual(
            serialize_date(d),
            {"$date": "2021-02-18T00:04:36.036+0100"}
        )

    def test_diecinueve(self):
        """default() with ISO datetime representation with TZ info without Epoch Aware without ms at the day edge
        """
        d = dt(1921, 2, 18, hour=0, minute=4, second=36, microsecond=0, tzinfo=GMT1())
        with self.assertRaises(ValueError):
            serialize_date(d)
        # self.assertEqual(
        #     serialize_date(d),
        #     {"$date": "1921-02-17T23:04:36Z"}
        # )

    def test_veinte(self):
        """default() with ISO datetime representation with TZ info without Epoch Aware with ms
        """
        d = dt(1921, 2, 18, hour=0, minute=4, second=36, microsecond=28000, tzinfo=GMT1())
        with self.assertRaises(ValueError):
            serialize_date(d)
        # self.assertEqual(
        #     serialize_date(d),
        #     {"$date": "1921-02-17T23:04:36.028Z"}
        # )

    def test_veintiuno(self):
        """default() with ISO datetime representation with TZ info (- timezone) with Epoch Aware with ms
        """
        d = dt(2021, 2, 18, hour=23, minute=4, second=36, microsecond=555000, tzinfo=GMT2())
        self.assertEqual(
            serialize_date(d),
            {"$date": "2021-02-18T23:04:36.555-0300"}
        )

    def test_veintidos(self):
        """default() with ISO datetime representation with TZ info (- timezone) without Epoch Aware with ms
        """
        d = dt(1921, 2, 18, hour=23, minute=4, second=36, microsecond=555000, tzinfo=GMT2())
        with self.assertRaises(ValueError):
            serialize_date(d)
        # self.assertEqual(
        #     serialize_date(d),
        #     {"$date": "1921-02-19T02:04:36.555Z"}
        # )

    def test_veintitres(self):
        """default() with ISO datetime representation with TZ info (+ timezone) with Epoch Aware with ms (year edge)
        """
        d = dt(2020, 12, 31, hour=23, minute=4, second=36, microsecond=123000, tzinfo=GMT1())
        self.assertEqual(
            serialize_date(d),
            {"$date": "2020-12-31T23:04:36.123+0100"}
        )

    def test_veintcuatro(self):
        """default() with ISO datetime representation with TZ info (- timezone) with Epoch Aware with ms (year edge)
        """
        d = dt(2021, 1, 1, hour=0, minute=4, second=36, microsecond=123000, tzinfo=GMT2())
        self.assertEqual(
            serialize_date(d),
            {"$date": "2021-01-01T00:04:36.123-0300"}
        )

    def test_veinticinco(self):
        """default() with ISO datetime representation with TZ info (custom timezone) with Epoch Aware with ms
        """
        d = dt(2021, 1, 1, hour=0, minute=4, second=36, microsecond=123000, tzinfo=CustomGMT())
        self.assertEqual(
            serialize_date(d),
            {"$date": "2021-01-01T00:04:36.123+0130"}
        )

    def test_veintiseis(self):
        """default() with ISO datetime representation with TZ info (custom timezone) with Epoch Aware with ms
        """
        d = dt(2021, 1, 1, hour=0, minute=4, second=36, microsecond=123000, tzinfo=CustomGMT2())
        self.assertEqual(
            serialize_date(d),
            {"$date": "2021-01-01T00:04:36.123-0130"}
        )

# TODO: 1. Add edge cases where month, year can be shifted (for year < 1970)
# TODO: 2. Add cases for unexpected exceptions and non supported libs exceptions

if __name__ == '__main__':
    unittest.main()
