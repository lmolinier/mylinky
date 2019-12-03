import unittest
import logging
import datetime

from mylinky.datedelta import datedelta

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
log = logging.getLogger("test")

class TestDateDelta(unittest.TestCase):

    def testDateDeltaStr(self):
        dd = datedelta(years=12)
        self.assertTrue("144 months" in str(dd))

        dd = datedelta(months=12)
        self.assertTrue("12 months" in str(dd))

        dd = datedelta(years=2, months=12)
        self.assertTrue("36 months" in str(dd), str(dd))

        dd = datedelta(years=2, months=6, days=3)
        self.assertTrue("30 months, 3 days" in str(dd), str(dd))

        dd = datedelta(years=2, months=1, seconds=15)
        self.assertTrue("25 months, 0:00:15" in str(dd), str(dd))

    def testDateDeltaAddYear(self):
        d = datetime.datetime(year=2011, month=12, day=9)
        dd = datedelta(years=8)
        r = d + dd
        log.debug(r)
        self.assertEqual(r, datetime.datetime.strptime("9/12/2019", "%d/%m/%Y"))

        d = datetime.datetime(year=2011, month=12, day=9)
        dd = datedelta(years=-8)
        r = d + dd
        log.debug(r)
        self.assertEqual(r, datetime.datetime.strptime("9/12/2003", "%d/%m/%Y"))

    def testDateDeltaAddMonth(self):
        d = datetime.datetime(year=2011, month=12, day=9)
        dd = datedelta(months=3)
        r = d + dd
        log.debug(r)
        self.assertEqual(r, datetime.datetime.strptime("9/3/2012", "%d/%m/%Y"))

        d = datetime.datetime(year=2011, month=5, day=9)
        dd = datedelta(months=3)
        r = d + dd
        log.debug(r)
        self.assertEqual(r, datetime.datetime.strptime("9/8/2011", "%d/%m/%Y"))

        d = datetime.datetime(year=2011, month=6, day=9)
        dd = datedelta(months=7)
        r = d + dd
        log.debug(r)
        self.assertEqual(r, datetime.datetime.strptime("9/1/2012", "%d/%m/%Y"))

        d = datetime.datetime(year=2011, month=12, day=9)
        dd = datedelta(months=-3)
        r = d + dd
        log.debug(r)
        self.assertEqual(r, datetime.datetime.strptime("9/9/2011", "%d/%m/%Y"))

        d = datetime.datetime(year=2011, month=5, day=9)
        dd = datedelta(months=-6)
        r = d + dd
        log.debug(r)
        self.assertEqual(r, datetime.datetime.strptime("9/11/2010", "%d/%m/%Y"))

        d = datetime.datetime(year=2011, month=5, day=9)
        dd = datedelta(months=-5)
        r = d + dd
        log.debug(r)
        self.assertEqual(r, datetime.datetime.strptime("9/12/2010", "%d/%m/%Y"))

    def testDateDeltaSub(self):
        d = datetime.datetime(year=2011, month=12, day=9)
        dd = datedelta(months=3)
        r = d - dd
        log.debug(r)
        self.assertEqual(r, datetime.datetime.strptime("9/9/2011", "%d/%m/%Y"))

        d = datetime.datetime(year=2011, month=12, day=9)
        dd = datedelta(years=1)
        r = d - dd
        log.debug(r)
        self.assertEqual(r, datetime.datetime.strptime("9/12/2010", "%d/%m/%Y"))

    def testDateDeltaMul(self):
        dd = datedelta(years=3)
        dd = dd * 5
        log.debug(dd)
        self.assertEqual(dd.months, 3*12*5)

if __name__ == "__main__":
    unittest.main()