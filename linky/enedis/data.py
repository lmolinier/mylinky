import logging
import requests
import datetime
from requests_toolbelt.utils import dump
import base64

log = logging.getLogger("enedis-data")

class DataException(Exception):
    pass

class Data:
    URL = 'https://espace-client-particuliers.enedis.fr/group/espace-particuliers/suivi-de-consommation'

    RESOURCE_HOURLY = "urlCdcHeure"
    RESOURCE_MONTHLY = "urlCdcMois"
    RESOURCE_YEARLY = "urlCdcAn"

    STEPS = {
        RESOURCE_HOURLY: datetime.timedelta(minutes=30),
        RESOURCE_MONTHLY: datetime.timedelta(hours=1),
        RESOURCE_YEARLY: datetime.timedelta(days=1),
    }

    def __init__(self, cookies, url=None):
        self.url = url if url is not None else Data.URL
        self.session = requests.Session()

        if cookies is not None:
            if type(cookies) != list:
                cookies = [cookies]
            for cookie in cookies:
                self.session.cookies.set_cookie(cookie)

        log.debug("Creating data (%s) with session %s" % (self.url, self.session))

    def get_data(self, resource, startDate=datetime.datetime(year=1970, month=1, day=1), endDate=datetime.datetime.today()):
        raw = self._query_data(resource, startDate, endDate)

        data = self._transform_data(resource, raw)
        return data

    def _transform_data(self, resource, raw):
        start = datetime.datetime.strptime(raw["periode"]["dateDebut"], "%d/%m/%Y")
        end = datetime.datetime.strptime(raw["periode"]["dateFin"], "%d/%m/%Y")
        step = Data.STEPS[resource]

        data = []
        for item in raw["data"]:
            rank = int(item["ordre"])-1
            value = float(item["valeur"])

            # Value is given in kW
            #  - if value is '-2', there is no value --> drop
            if str(item["valeur"]) == "-2":
                continue

            data.append({'date': start + (rank*step), 'value': value, 'type': 'normales', 'price': 0.0})

        return data

    def _query_data(self, resource, startDate, endDate):

        self.session.headers.update({'User-agent': "linky crawler"})
        payload = {
            '_lincspartdisplaycdc_WAR_lincspartcdcportlet_dateDebut': startDate.strftime("%d/%m/%Y"),
            '_lincspartdisplaycdc_WAR_lincspartcdcportlet_dateFin': endDate.strftime("%d/%m/%Y")
        }

        params = {
            'p_p_id': 'lincspartdisplaycdc_WAR_lincspartcdcportlet',
            'p_p_lifecycle': 2,
            'p_p_state': 'normal',
            'p_p_mode': 'view',
            'p_p_resource_id': resource,
            'p_p_cacheability': 'cacheLevelPage',
            'p_p_col_id': 'column-1',
            'p_p_col_pos': 1,
            'p_p_col_count': 3
        }

        log.info("Sending data request for resource %s (%s - %s)" % (resource, startDate, endDate))
        resp = self.session.post(self.url, data=payload, params=params, allow_redirects=False)

        if 300 <= resp.status_code < 400:
            # It appears that it is frequent to get first a 302, even if the request is correct
            # #nocomment
            resp = self.session.post(self.url, data=payload, params=params, allow_redirects=False)

        log.debug("resp: %s" % dump.dump_response(resp).decode('utf-8'))
        body = resp.json()

        if body["etat"]["valeur"] == "erreur":
            raise DataException("Error on server when retrieving data: %s" % body["etat"]["erreurText"])

        if body["etat"]["valeur"] not in ["termine"]:
            raise DataException("Invalid response state code '%s'" % body["etat"]["valeur"])

        return body["graphe"]

