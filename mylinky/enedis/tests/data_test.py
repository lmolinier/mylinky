import unittest
import datetime
import requests
import responses
import logging
import json

from mylinky.enedis import Data

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
log = logging.getLogger("test")

class TestData(unittest.TestCase):

    @responses.activate
    def testQueryData(self):
        cookie = requests.cookies.create_cookie(domain="testme", name="iPlanetDirectoryPro", value="fakecookievalue")

        l = Data(cookies=cookie, url="http://testme/data")
        
        responses.add(responses.POST, "http://testme/data", 
            status=200,
            json={
                "etat": { "valeur": "termine" },
                "graphe": {
                    "decalage": 0,
                    "puissanceSouscrite": 9,
                    "periode": {
                        "dateFin": "14/11/2019",
                        "dateDebut": "11/11/2019"
                    },
                    "data": [ 
                        {"valeur": 4.154, "ordre": 1},
                        {"valeur": 4.508, "ordre": 2},
                        {"valeur": 4.210, "ordre": 3},
                        {"valeur": 4.322, "ordre": 4},
                        {"valeur": 4.382, "ordre": 5}
                    ]
                }
            })
        
        data = l._query_data("testresource", datetime.datetime(2019, 1, 1), datetime.datetime(2019, 1, 1))

        # Check request
        self.assertEqual(len(responses.calls), 1)
        self.assertTrue(responses.calls[0].request.url.startswith("http://testme/data"))
        self.assertEqual(len(responses.calls[0].request._cookies), 1)
        self.assertTrue("iPlanetDirectoryPro" in responses.calls[0].request._cookies)

        self.assertTrue("data" in data)
        self.assertEqual(len(data["data"]), 5)

    def testTransformData(self):
        test_data = {
            "etat": { "valeur": "termine" },
            "graphe": {
                "decalage": 0,
                "puissanceSouscrite": 9,
                "periode": {
                    "dateFin": "14/11/2019",
                    "dateDebut": "11/11/2019"
                },
                "data": [ 
                    {"valeur": 4.154, "ordre": 1},
                    {"valeur": 4.508, "ordre": 2},
                    {"valeur": 4.210, "ordre": 3},
                    {"valeur": 4.322, "ordre": 4},
                    {"valeur": 4.382, "ordre": 5}
                ]
            }
        }

        l = Data(cookies=None, url="http://testme/data")

        data = l._transform_data(Data.RESOURCE_HOURLY, test_data["graphe"])
        log.debug(data)
        self.assertEqual(len(data), 5)
        self.assertEqual(data[0]["date"], datetime.datetime.strptime("11/11/2019 00:30", "%d/%m/%Y %H:%M"))
        self.assertEqual(data[0]["value"], 4.154)
        self.assertEqual(data[4]["date"], datetime.datetime.strptime("11/11/2019 02:30", "%d/%m/%Y %H:%M"))
        self.assertEqual(data[4]["value"], 4.382)

    def testTransformDataIncompeteGraphe(self):
        test_data = {
            "etat": { "valeur": "termine" },
            "graphe": {
                "decalage": 3,
                "puissanceSouscrite": 9,
                "periode": {
                    "dateFin": "14/11/2019",
                    "dateDebut": "11/11/2019"
                },
                "data": [ 
                    {"valeur": -1, "ordre": 1},
                    {"valeur": -1, "ordre": 2},
                    {"valeur": 4.210, "ordre": 3},
                    {"valeur": -1, "ordre": 4},
                    {"valeur": -1, "ordre": 5}
                ]
            }
        }

        l = Data(cookies=None, url="http://testme/data")
        data = l._transform_data(Data.RESOURCE_HOURLY, test_data["graphe"])
        log.debug(data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["date"], datetime.datetime.strptime("11/11/2019 00:30", "%d/%m/%Y %H:%M"))
        self.assertEqual(data[0]["value"], 4.210)

    def testTransformYearly(self):
        test_data = json.loads('{"etat":{"valeur":"termine"},"graphe":{"decalage":0,"puissanceSouscrite":0,"periode":{"dateFin":"02/12/2019","dateDebut":"02/12/2016"},"data":[{"valeur":-2,"ordre":0},{"valeur":-2,"ordre":1},{"valeur":4148.506,"ordre":2},{"valeur":11327.075,"ordre":3}]}}')
        l = Data(cookies=None, url="http://testme/data")
        data = l._transform_data(Data.RESOURCE_YEARLY, test_data["graphe"], (datetime.datetime(year=2018, month=1, day=1), datetime.datetime(year=2018, month=12, day=31)))
        log.debug(data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["date"], datetime.datetime.strptime("1/1/2018 00:0", "%d/%m/%Y %H:%M"))
        self.assertEqual(data[0]["value"], 4148.506)

    def testTimesheetEmpty(self):
        l = Data(cookies=None, url="http://testme/data")
        t = l._get_type(datetime.datetime(2019,1,1,1,30))
        self.assertEqual(t, "normale")

    def testTimesheet(self):
        timesheet = [("00:00", "06:30")]
        l = Data(cookies=None, url="http://testme/data", timesheet=timesheet)
        t = l._get_type(datetime.datetime(2019,1,1,1,30))
        self.assertEqual(t, "normale")


if __name__ == "__main__":
    unittest.main()