import unittest
import datetime
import requests
import responses
import logging

from linky.enedis import Data

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
log = logging.getLogger("test")

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
        l = Data(cookies=None, url="http://testme/data")

        data = l._transform_data(Data.RESOURCE_HOURLY, test_data["graphe"])
        log.debug(data)


if __name__ == "__main__":
    unittest.main()