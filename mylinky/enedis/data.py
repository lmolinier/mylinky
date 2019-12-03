import logging
import requests
import datetime
from requests_toolbelt.utils import dump
import base64

from mylinky.datedelta import datedelta

log = logging.getLogger("enedis-data")

class DataException(Exception):
    pass

class Data:
    URL = 'https://espace-client-particuliers.enedis.fr/group/espace-particuliers/suivi-de-consommation'

    RESOURCE_HOURLY = "urlCdcHeure"
    RESOURCE_MONTHLY = "urlCdcMois"
    RESOURCE_YEARLY = "urlCdcAn"

    STEPS = {
        RESOURCE_HOURLY: datedelta(minutes=30),
        RESOURCE_MONTHLY: datedelta(months=1),
        RESOURCE_YEARLY: datedelta(years=1),
    }

    def __init__(self, cookies, timesheet=None, url=None):
        self.url = url if url is not None else Data.URL
        self.session = requests.Session()
        self.timesheet = timesheet

        if cookies is not None:
            if type(cookies) != list:
                cookies = [cookies]
            for cookie in cookies:
                self.session.cookies.set_cookie(cookie)

        log.debug("Creating data (%s) with session %s" % (self.url, self.session))

    def get_data(self, resource, startDate=datetime.datetime(year=1970, month=1, day=1), endDate=datetime.datetime.today()):
        raw = self._query_data(resource, startDate, endDate)

        data = self._transform_data(resource, raw, (startDate, endDate))
        return data

    def _get_type(self, startdate):
        daytime = startdate.time()
        if self.timesheet is None:
            return "normale"
        
        for (stime, etime) in self.timesheet:
            pass

        return "normale"

        

    def _transform_data(self, resource, raw, bounds=None):
        start = datetime.datetime.strptime(raw["periode"]["dateDebut"], "%d/%m/%Y")
        end = datetime.datetime.strptime(raw["periode"]["dateFin"], "%d/%m/%Y")
        step = Data.STEPS[resource]

        if resource == Data.RESOURCE_YEARLY:
            start = start.replace(day=1, month=1)
            end = end.replace(day=1, month=1) - datetime.timedelta(days=1)


        data = []
        offset = raw["decalage"] - 1 if raw["decalage"]>0 else 0
        for item in raw["data"]:
            rank = int(item["ordre"])

            # correct the start with the 'decalage' field for incomplete graphe
            if rank < offset:
                continue
            rank = rank - offset
            value = float(item["valeur"])

            begin = start + (rank*step)
            end = start + ((rank+1)*step)
            duration = end - begin

            if bounds and (begin < bounds[0] or begin >= bounds[1]):
                continue

            # Value is given in kW
            #  - if value is '-2', there is no value --> drop
            #  - if value is '-1', TODO
            if item["valeur"] < 0:
                continue
            d = {'date': begin, 'duration': duration.total_seconds(), 'value': value}
            if resource == Data.RESOURCE_HOURLY:
                d.update({'type': self._get_type(start + (rank*step))})
            data.append(d)

        return data

    def _query_data(self, resource, startDate, endDate):

        self.session.headers.update({'User-agent': "mylinky"})
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
            raise DataException("Error on server when retrieving data: %s" % body["etat"]["erreurText"] if "erreurText" in body["etat"] else "n/a")

        if body["etat"]["valeur"] not in ["termine"]:
            raise DataException("Invalid response state code '%s'" % body["etat"]["valeur"])

        return body["graphe"]

